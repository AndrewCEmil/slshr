import os
import logging
import pymongo
import whirlpool
import datetime

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import view_config
from bson.objectid import ObjectId
from pyramid.security import (
        authenticated_userid,
        remember,
        forget,
        )

from wsgiref.simple_server import make_server

logging.basicConfig(filename="tasks.py"+'.log', level=logging.DEBUG)
logger = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

dbconn = pymongo.Connection()
db = dbconn['list']
#schema: _id: default, name: string, closed = bool
coll = db['tasks']
#schema: _id: default, author:string
playcoll = db['playlists']
#schema: _id: username, hash: string, salt: string
usercoll = db['users']
#schema: _id default, url: string, headline: string, insertts: timestamp
#thats schema for the playlist where the collection name is the curator
#schema: _id: username, followts = timestamp followers = [{ username: username, followts: timestamp }]
followcoll = db['followers']


# views

@view_config(route_name='home')
def home_view(request):
    logger.info('in home view')
    #TODO select a random playlist
    #for now redirect to playlists
    return HTTPFound(location=request.route_url('playlists'))
    

@view_config(route_name='playlists', renderer='playlists.mako')
def playlists_view(request):
    logger.info("in playlists view")
    playlists = []
    logger.info("finding playlists")
    for playlist in playcoll.find():
        logger.info(playlist)
        playlists.append(playlist)
    return { "playlists" : playlists }

@view_config(route_name='playlist', renderer='playlist.mako')
def playlist_view(request):
    logger.info("in playlist view")
    articles = []
    logger.info("finding playlist")
    playlist_name = request.matchdict['name']
    playlist_col = db[playlist_name]
    for article in playlist_col.find():
        articles.append(article)
        logger.info(article['headline'])
    return { "articles" : articles, "name" : playlist_name }

@view_config(route_name='newuser', renderer='newuser.mako')
def new_user_view(request):
    logger.info("in new user view")
    username = authenticated_userid(requests)
    if username != "ace":
        return notfound_view(request)
    if request.method == 'POST':
        #validate input
        newusername = request.POST.get('newusername')
        newuserpass = request.POST.get('newuserpass')
        listname = request.POST.get('listname')
        if newusername is not None and newuserpass is not None and listname is not None:
            #generate hash
            salt = gensalt()
            wp = whirlpool.new("" + newuserpass + salt)
            passhash = wp.hexdigest()
            #insert into db
            usercoll.insert({"_id": newusername, "hash": passhash, "salt": salt, "groups": ["admin"]})
            playcoll.insert({'name' : listname, 'author' : newusername})
            request.session.flash("user created")
        else:
            request.session.flash('Please fill out all the fields')
    return {}

@view_config(route_name='edit', renderer="edit.mako")
def edit_view(request):
    logger.info('in edit view')
    username = authenticated_userid(request)
    if username is None:
        return HTTPFound(location=request.route_url('login'))    
    playlist_col = db[username]
    
    articles = []
    for article in playlist_col.find():
        articles.append(article)

    if request.method == 'POST':
        headline = reqeust.POST.get('linkname')
        url = request.POST.get('url')
        if headline is None or url is None:
            request.session.flash('Please fill out all the fields')
        else:
            ts = datetime.datetime.utcnow()
            newarticle = {'url': url, 'headline': headline, 'timestamp': ts}
            articles.append(newarticle)
            playlist_col.insert(newarticle)
    logger.debug('returning from edit')
    return {'name': username, 'articles': articles}

"""
@view_config(route_name='follow', renderer='follow.mako')
def follow():
    username = authenticated_userid(request)
    if username is None:
        #TODO generic follow page
    if request.method != "POST":
        #return follow.mako
        #TODO
"""


#this is the post-only endpoint that should not be linked to, but used for sending data to
@view_config(route_name="followreq", request_method='POST')
def follow_request(request):
    logger.info('got a follow request')
    username = authenticated_userid(request)
    if username is None:
        logger.warning("got a request to follow without a username")
        request.session.flash("need to be logged in to follow")
        return HTTPFound(location=request.current_route_url())

    followee = request.POST.get('followee')
    if followee is None:
        logger.warning("got a request to follow but no followee")
        request.session.flash("need to follow a user lol")
        return HTTPFound(location=request.current_route_url())

    #first verify that this is a user we are following
    if usercoll.find({"_id" : followee}).count() == 0:
        #not a real user to follow
        logger.warning(username + " just tried to follow " + followee + " but not found")
        request.session.flash("found no users named " + followee)
        return HTTPFound(location=request.current_route_url())
    if usercoll.find({'_id' : followee}).count() > 1:
        #BADBADBAD
        logger.error("multiple users in usercoll with name " + followee)
        return HTTPFound(location=request.current_route_url())
    
    #find the followcoll document to update
    fcount = followcoll.find({'_id': followee}).count() 
    ts = datetime.datetime.utcnow()
    if fcount > 1:
        #BADBADBAD
        logger.error("mutliple users in followcoll with name " + followee)
        return HTTPFound(location=request.current_route_url())
    elif fcount == 1:
        followcoll.update({'_id': followee},{"$push" : { "followers": { "username": username, "followts": ts}}})
    elif fcount == 0:
        #need to create follower index for 
        #TODO remove and add at user creation time 
        followcoll.insert({'_id': followee, 'followers': [ { "username": username, "followts": ts}]})
        
    #and done!
    return HTTPFound(location=request.current_route_url())

@view_config(route_name='followers', renderer='followers.mako')
def followers_view(request):
    logger.info("in followers view")
    username = request.matchdict['followee']
    count = followcoll.find({'_id': username}).count()
    if count == 0:
        #empty return TODO
        followers =[]
    elif count == 1:
        followers = followcoll.find({'_id':username})[0]['followers']
    else:
        logger.error('got more than one use in followcoll in followers_view')
        followers = []
    return {'followers': followers}


@view_config(route_name='login', renderer='login.mako') 
def login_view(request): 
    logger.info('in login view') 
    #get login info 
    if request.method == 'POST':
        #validate input
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username is not None and password is not None:
            #check authentication
            check = credcheck(username, password)
            if check is True:
                #redirect to edit page
                headers = remember(request, username)
                return HTTPFound(location=request.route_url('edit'), headers=headers)
            else:
                #fail and flash retry
                request.session.flash('Please enter valid credentials')
        else:
            request.session.flash('Please fill in all the fields')
    return {}

@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(request):
    request.response.status = '404 Not Found'
    return {}


def usercheck(creds, request):
    return credcheck(creds['login'], creds['password'])

def credcheck(login, password):
    #first lookup in db and validate
    cursor = usercoll.find({"_id" : login})
    if cursor.count() == 0:
        logger.info("looked up " + login + ", found 0 users")
        return False
    if cursor.count() > 1:
        logger.warning("looked up " + login + ", found multiple users!")
        return False
    userdoc = cursor[0]
    #now generate the hash 
    wp = whirlpool.new("" + password + userdoc['salt'])
    passhash = wp.hexdigest()
    if passhash == userdoc['hash']:
        return True 
    return False

def gensalt():
    return os.urandom(512).encode('base64')#length of the hash output i think...

