import os
import logging
import pymongo

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import view_config
from bson.objectid import ObjectId

from wsgiref.simple_server import make_server


logging.basicConfig(filename='tasks.log', level=logging.DEBUG)
logger = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

dbconn = pymongo.Connection()
db = dbconn['list']
#schema: _id: default, name: string, closed = bool
coll = db['tasks']
#schema: _id: default, name: string, author:string
playcoll = db['playlists']
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

""" TODO new playslists
@view_config(route_name='newplaylist', renderer='new.mako')
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


if __name__ == '__main__':
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here, 'templates')
    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    # configuration setup
    config = Configurator(settings=settings, session_factory=session_factory)
    # routes setup
    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('playlists', '/people')
    config.add_route('close', '/close/{id}')
    config.add_route('playlist', '/playlist/{name}')
    # static view setup
    config.add_static_view('static', os.path.join(here, 'static'))
    # scan for @view_config and @subscriber decorators
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
