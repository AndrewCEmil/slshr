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


logging.basicConfig(filename='tasks2.log', level=logging.DEBUG)
logger = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

#schema: _id: default, name: string, closed = bool
dbconn = pymongo.Connection()
db = dbconn['list']
coll = db['tasks']

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
    config.add_route('close', '/close/{id}')
    # static view setup
    config.add_static_view('static', os.path.join(here, 'static'))
    # scan for @view_config and @subscriber decorators
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
