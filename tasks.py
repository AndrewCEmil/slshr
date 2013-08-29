import os
import logging
import pymongo
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

from userops import *

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
#schema: _id: username, followts = timestamp followers = [{ username: username, followts: timestamp }] #TODO check this schema
followcoll = db['followers']
#schema: _id: username, following = [{ username: username, followts: timestamp }]
followingcol = db['following']


@view_config(route_name='home')
def home_view(request):
    logger.info('in home view')
    #TODO select a random playlist
    #for now redirect to playlists
    return HTTPFound(location=request.route_url('playlists'))
    

#TODO this should be pulled out of the view
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
    username = request.matchdict['name']
    if username is None:
        #TODO what is the proper behavior here?
        #probably a redirect + a flash
        logger.error('got a playlist request where name is None')
    articles = get_user_articles(username)
    return { "articles" : articles, "name" : username }

@view_config(route_name='newuser', renderer='newuser.mako')
def new_user_view(request):
    logger.info("in new user view")
    username = authenticated_userid(request)
    if username != "ace":
        return notfound_view(request)
    if request.method == 'POST':
        #validate input
        newusername = request.POST.get('newusername')
        newuserpass = request.POST.get('newuserpass')
        if newusername is None or newuserpass is None:
            request.session.flash('please fill out all the fields')
        elif user_exists(newusername):
            request.session.flash('Username already taken :(')
        elif not create_new_user(newusername, newuserpass):
            request.session.flash('error creating user...strange')
        else:
            request.session.flash('successfuly created!')
        return {}

@view_config(route_name='edit', renderer="edit.mako")
def edit_view(request):
    logger.info('in edit view')
    username = authenticated_userid(request)
    #if username is None:
    #    return HTTPFound(location=request.route_url('login'))    
    if not user_exists(username):
        return HTTPFound(location=request.route_url('login'))
    articles = get_user_articles(username)

    if request.method == 'POST':
        headline = request.POST.get('linkname')
        url = request.POST.get('url')
        new_user_article = insert_user_article(username, headline, url)
        if new_user_article is None:
            request.sessision.flash('Please enter a valid article')
            return HTTPFound(location=request.current_route_url())
        else:
            articles.append(new_user_article)
    logger.debug('returning from edit')
    return {'name': username, 'articles': articles}

#TODO here we need to provide better responses back
#how to respond in ajax requests?
#this is the post-only endpoint that should not be linked to, but used for sending data to
@view_config(route_name="followreq", request_method='POST')
def follow_request(request):
    logger.info('got a follow request')
    username = authenticated_userid(request)
    followee = request.POST.get('followee')
    if not user_exists(username):
        request.session.flash('need to be logged in to follow')
        return HTTPFound(location=request.current_route_url())
    if not user_exists(followee):
        request.session.flash('need to follow an actual user')
        return HTTPFound(location=request.current_route_url())
    if not new_follow(username, followee):
        #TODO better info to user here
        request.session.flash('following failed')
        return HTTPFound(location=request.current_route_url())
    else:
        request.session.flash('followed successfully')
    #and done!
    return HTTPFound(location=request.current_route_url())

#TODO need to pull this into userops
#how to alert users on ajax responses?
#again, only an endpoint
@view_config(route_name='unfollowreq', request_method='POST')
def unfollow_reqeust(request):
    logger.info('got an unfollow request')
    #get username
    username = authenticated_userid(request)
    followee = request.POST.get('unfollowee')
    if not user_exists(username):
        request.session.flash('need to be logged in to unfollow')
        return HTTPFound(location=request.current_route_url())
    if not user_exists(followee):
        request.session.flash('need to to unfollow an actual user')
        return HTTPFound(location=request.current_route_url())
    if not unfollow(username, followee):
        logger.debug('unfollowed failed!')
        request.session.flash('unfollowing failed')
        return HTTPFound(location=request.current_route_url())

    logger.debug('unfollowed successfully!')
    return HTTPFound(location=request.current_route_url())

"""
    if username is None:
        logger.warning('got a request to unfollow without a username')
        request.session.flash('need to be logged in to unfollow')
        return HTTPFound(location=request.current_route_url())
    #and verify we got a real user
    #TODO verify the username is a real user
    #TODO pull out that check into a method

    #and verify we got a real user unfollowee
    unfollowee = request.POST.get('unfollowee')
    usercount = usercoll.find({'_id': unfollowee}).count()
    if usercount == 0:
        logger.warning(username + " just tried to unfollow a not real user: " + unfollowee)
        return HTTPFound(location=request.current_route_url())
    if usercount > 1:
        logger.error(str(usercount) + " users with name " + unfollowee)
        return HTTPFound(location=request.current_route_url())

    if unfollowee is None:
        logger.warning('got a request to unfollow but no followee')
        request.session.flash('need to unfollow a user lol')
        return HTTPFound(location=reqeuest.current_route_url()) 
    
    followcount = followcoll.find({'_id': unfollowee}).count()
    followingcount = followingcol.find({'_id': username}).count()
    if followcount > 1:
        logger.error('multiple users in followcoll with name ' + unfollowee)
    elif followingcount > 1:
        logger.error('multiple users in followingcol with name ' + username)
    elif followingcount == 0:
        logger.error('no users in followcoll with name ' + unfollowee)
    elif followingcount == 0:
        logger.errro('no users in folowingcol with name ' + username)
    else:
        #found exactly one user and one followee
        logger.info('finally unfollowing completely')
        #remove username from followees followers list
        followcoll.update({'_id': unfollowee}, {'$pull': { 'followers': { 'username': username}}})
        #remove followee from users following list
        followingcol.update({'_id': username}, {'$pull': { 'following': { 'username': unfollowee}}})
    #and done
    return HTTPFound(location=request.current_route_url())
"""
    
    
@view_config(route_name='followers', renderer='followers.mako')
def followers_view(request):
    logger.info("in followers view")
    username = request.matchdict['followee']
    if not user_exists(username):
        return {'followers': [], 'name': username}
    followers = get_user_followers(username)
    return {'followers': followers, 'name': username}

@view_config(route_name='following', renderer='following.mako')
def following_view(request):
    logger.info("in following view")
    username = request.matchdict['follower']
    if not user_exists(username):
        #TODO need better behavior here probably a redirect
        return {'followers': [], 'name': username}

    following = get_user_following(username)
    return {'following': following, 'name': username}

@view_config(route_name='feed', renderer='feed.mako')
def feed_view(request):
    logger.info('in feed view')
    feeduser = request.matchdict['name']
    if not user_exists(feeduser):
        request.session.flash('need to look at a real users feed')
        return HTTPFound(location=request.route_url('/people'))

    selections = generate_feed(feeduser)
    return {"selections": selections, "name": feeduser}

#NOTE: assumes feeduser is a real user
def generate_feed(feeduser):
    #first get all people they are following
    following = get_user_following(feeduser)
    #create a list of all the articles from all those users
    selections = []
    for user in following:
        articles = get_user_articles(user['username'])
        for article in articles:
            article['author'] = user['username']
        selections = selections + articles

    #sort the list
    selections.sort(key=lambda selection: selection['timestamp'])
    return selections
    


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

