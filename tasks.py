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
from security import BasicAuthenticationPolicy

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

#TODO how to make this authenticated?
@view_config(route_name='newuser', renderer='newuser.mako')
def new_user_view(request):
    logger.info("in new user view")
    if request.method == 'POST':
        #validate input
        username = request.POST.get('username')
        userpass = request.POST.get('userpass')
        listname = request.POST.get('listname')
        if username is not None and userpass is not None and listname is not None:
            #generate hash
            salt = gensalt(username)
            wp = whirlpool.new(userpass + salt)
            passhash = wp.hexdigest()
            #insert into db
            usercoll.insert({"_id": username, "hash": passhash, "salt": salt, "groups": ["admin"]})
            playcoll.insert({'name' : listname, 'author' : username})
            #send user to edit page view
            return HTTPFound(location=request.route_url('editlist', name=username))
        else:
            request.session.flash('Please fill out all the fields')
    return {}

#TODO how to make this authenticated?
@view_config(route_name='editlist', renderer='editlist.mako')
def edit_list_view(request):
    logger.info('in edit list view')
    articles = []
    authorname = request.matchdict['name']
    if authorname is None:
        logger.error("got into editlist without an authorname")
        print "ZOMG"
    print authorname
    playlist_col = db[authorname]
    for article in playlist_col.find():
        articles.append(article)
    if request.method == 'POST':
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

@view_config(route_name='close')
def close_view(request):
    logger.info("in close view")
    task_id = ObjectId(request.matchdict['id'])
    coll.update({"_id" : task_id}, { '$set' : { "closed" : True } })
    request.session.flash('task was closed!')
    return HTTPFound(location=request.route_url('list'))


@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(request):
    request.response.status = '404 Not Found'
    return {}


def usercheck(creds, request):
    return credcheck(creds['login'], creds['password'])

#TODO cred_check:
def credcheck(login, password):
    #first lookup in db and validate
    cursor = usercoll.find({"_id" : login})
    if cursor.count() == 0:
        logger.info("looked up " + login + ", found 0 users")
        return None
    if cursor.count() > 1:
        logger.warning("looked up " + login + ", found multiple users!")
        return None
    userdoc = cursor[0]
    #now generate the hash 
    wp = whirlpool.new(password + userdoc['salt'])
    passhash = wp.hexdigest()
    if passhash == userdoc['hash']:
        return userdoc['groups']
    else:
        return None

#TODO
def gensalt(usersalt):
    return "potato"

if __name__ == '__main__':
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here, 'templates')
    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    # configuration setup
    config = Configurator(settings=settings, session_factory=session_factory,
                          authentication_policy=BasicAuthenticationPolicy(usercheck))
    # routes setup
    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('playlists', '/people')
    config.add_route('close', '/close/{id}')
    config.add_route('playlist', '/playlist/{name}')
    config.add_route('newuser', '/newuser')
    config.add_route('editlist', '/playlist/{name}/edit')
    # static view setup
    config.add_static_view('static', os.path.join(here, 'static'))
    # scan for @view_config and @subscriber decorators
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
