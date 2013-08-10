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


logging.basicConfig(filename=__file__+'.log', level=logging.DEBUG)
logger = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

dbconn = pymongo.Connection()
db = dbconn['list']
#schema: _id: default, name: string, closed = bool
coll = db['tasks']
#schema: _id: default, name: string, author:string
playcoll = db['playlists']
#schema: _id: username, hash: string, salt: string, groups: list[string]
usercoll = db['users']

#schema: _id default, url: string, headline: string, insertts: timestamp
#thats schema for the playlist where the collection name is the curator

# views
"""
@view_config(route_name='list', renderer='list.mako')
def list_view(request):
    logger.info("in list view")
    tasklist = []
    logger.info(coll.find().count())
    logger.info("finding tasks")
    for task in coll.find():
        if not task["closed"]:
            tasklist.append(task)
    return { "tasks" : tasklist }
""" 

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


"""
@view_config(route_name='new', renderer='new.mako')
def new_view(request):
    logger.info("in new view")
    if request.method == 'POST':
        if request.POST.get('name'):
            logger.info("inserting")
            coll.insert({ "name": request.POST.get('name'), "closed": False})
            request.session.flash('New task was successfully added!')
            return HTTPFound(location=request.route_url('list'))
        else:
            request.session.flash('Please enter a name for the task!')
    return {}
"""

#TODO how to make this authenticated?
@view_config(route_name='newuser', renderer='newuser.mako')
def new_user_view(request):
    logger.info("in new user view")
    if request.method == 'POST':
        #validate authentication 
        username = request.POST.get('username')
        userpass = request.POST.get('userpass')
        if not credcheck(username, userpass):
            request.session.flash('Authentication failed')
            return {}
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
            #send user to edit page view
            return HTTPFound(location=request.route_url('editlist', name=newusername))
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
@view_config(route_name='editlist', renderer='editlist.mako')
def edit_list_view(request):
    logger.info('in edit list view')
    articles = []
    username = authenticated_userid(request)
    if username:
        print username
        print "WIN"
    authorname = request.matchdict['name']
    if authorname is None:
        logger.error("got into editlist without an authorname")
        print "ZOMG"
        return {}
    playlist_col = db[authorname]
    for article in playlist_col.find():
        articles.append(article)
    if request.method == 'POST':
        #authorize
        username = request.POST.get('username')
        userpass = request.POST.get('userpass')
        if username != authorname or not credcheck(username, userpass):
            request.session.flash('Authentication failed')
            return {"name" : authorname, "articles" : articles}
        #validate
        headline = request.POST.get('linkname')
        url = request.POST.get('url')
        if headline is not None and url is not None:
            #generate new article entry
            ts = datetime.datetime.utcnow()
            newarticle = {"url" : url, "headline" : headline, "timestamp" : ts}
            #push link onto list
            articles.append(newarticle)
            #add into database
            playlist_col.insert(newarticle)
        else:
            request.session.flash('Please fill in all the fields')
    #get playlist generate articles list
    logger.debug("returning from edit list")
    logger.debug({"name" : authorname, "articles": articles})
    return {"name" : authorname, "articles": articles}
"""

#TODO add to authentication
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
                playlistinfo = playcoll.find({'author' : username})[0]
                playlistname = playlistinfo['name']
                return HTTPFound(location=request.route_url('edit'), headers=headers)
            else:
                #fail and flash retry
                request.session.flash('Please enter valid credentials')
        else:
            request.session.flash('Please fill in all the fields')
    return {}

"""
@view_config(route_name='close')
def close_view(request):
    logger.info("in close view")
    task_id = ObjectId(request.matchdict['id'])
    coll.update({"_id" : task_id}, { '$set' : { "closed" : True } })
    request.session.flash('task was closed!')
    return HTTPFound(location=request.route_url('list'))
"""


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

