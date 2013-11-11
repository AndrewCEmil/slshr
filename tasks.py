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
    playlists = get_all_playlists()
    loggedin = False
    user = authenticated_userid(request)
    if user is not None:
        loggedin = True
    return { "playlists" : playlists, "listname":"Playlists", "loggedin": loggedin}

@view_config(route_name='playlist', renderer='playlist.mako')
def playlist_view(request):
    logger.info("in playlist view")
    loggedin = False
    username = authenticated_userid(request)
    userfollows = False
    reqname = request.matchdict['name']
    if reqname is None:
        #TODO what is the proper behavior here?
        #probably a redirect + a flash
        logger.error('got a playlist request where name is None')
    if username:
        loggedin = True
        userfollows = follows(username, reqname)
    articles = get_user_articles(reqname)
    return { "articles" : articles, "name" : reqname, "loggedin": loggedin, "userfollows": userfollows, "listname": "list" }

@view_config(route_name='newuser', renderer='newuser.mako')
def new_user_view(request):
    logger.info("in new user view")
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
            remember(request, newusername)
            return HTTPFound(location=request.route_url('edit'))
    return {}

@view_config(route_name='edit', renderer="edit.mako")
def edit_view(request):
    logger.info('in edit view')
    username = authenticated_userid(request)
    if not user_exists(username):
        return HTTPFound(location=request.route_url('login'))
    articles = get_user_articles(username)

    if request.method == 'POST':
        headline = request.POST.get('linkname')
        url = request.POST.get('url')
        new_user_article = insert_user_article(username, headline, url)
        if new_user_article is None:
            request.session.flash('Please enter a valid article')
            return HTTPFound(location=request.current_route_url())
        else:
            #add the article in for displaying to user without a full reload
            articles.insert(0,new_user_article)
    logger.debug('returning from edit')
    return {'name': username, 'articles': articles, "loggedin": True, "userfollows": True, "listname": "edit"}

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

#TODO how to make this more secure?
#deletes an entry from a users list
@view_config(route_name="deleteid", request_method="POST")
def delete_req_id(request):
    logger.info("got a delete id request")
    username = authenticated_userid(request)
    if username is None:
        request.session.flash("need to be logged in to edit")
        return HTTPFound(location=request.current_route_url())
    targetid = request.POST.get("targetid")
    if targetid is None:
        return HTTPFound(location=request.current_route_url())

    logger.debug("calling delete_user_article_by_id")
    delete_user_article_by_id(username, targetid)
    return HTTPFound(location=request.current_route_url())

#TODO how to make this more secure?
#deletes an entry from a users list
@view_config(route_name="deleteidx", request_method="POST")
def delete_req(request):
    logger.info("got a delete idx request")
    username = authenticated_userid(request)
    if username is None:
        request.session.flash("need to be logged in to edit")
        return HTTPFound(location=request.current_route_url())
    targetidx = request.POST.get("targetidx")
    if targetidx is None:
        return HTTPFound(location=request.current_route_url())

    logger.debug("calling delete_user_article_by_idx")
    delete_user_article_by_idx(username, int(targetidx))
    return HTTPFound(location=request.current_route_url())


@view_config(route_name='followers', renderer='followers.mako')
def followers_view(request):
    logger.info("in followers view")
    username = request.matchdict['followee']
    if not user_exists(username):
        return {'followers': [], 'name': username}
    followers = get_user_followers(username)

    user = authenticated_userid(request)
    loggedin = False
    userfollows = False
    if user is not None:
        loggedin = True
        userfollows = follows(user, username) 
    return {'followers': followers, 'name': username, "listname":"followers", "loggedin": loggedin, "userfollows": userfollows}

@view_config(route_name='following', renderer='following.mako')
def following_view(request):
    logger.info("in following view")
    username = request.matchdict['follower']
    if not user_exists(username):
        #TODO need better behavior here probably a redirect
        return {'followers': [], 'name': username}

    user = authenticated_userid(request)
    loggedin = False
    userfollows = False
    if user is not None:
        loggedin = True
        userfollows = follows(user, username) 
    following = get_user_following(username)
    return {'following': following, 'name': username, "listname": "followees", "loggedin": loggedin, "userfollows": userfollows}

@view_config(route_name='feed', renderer='feed.mako')
def feed_view(request):
    logger.info('in feed view')
    feeduser = request.matchdict['name']
    if not user_exists(feeduser):
        request.session.flash('need to look at a real users feed')
        return HTTPFound(location=request.route_url('/people'))

    user = authenticated_userid(request)
    loggedin = False
    userfollows = False
    if user is not None:
        loggedin = True
        userfollows = follows(user, feeduser) 
    selections = generate_feed(feeduser)
    return {"selections": selections, "name": feeduser, "listname": "feed", "loggedin": loggedin, "userfollows": userfollows}

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
    selections.reverse()
    return selections
    

@view_config(route_name='logout')
def logout_view(request):
    logger.info('in logout view')
    user = authenticated_userid(request)
    if user is None:
        request.session.flash("need to be logged in to log out, lol")
    else:
        forget(request)
    return HTTPFound(location=request.route_url('playlists'))

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

