import os
import logging
import pymongo

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from wsgiref.simple_server import make_server

logging.basicConfig(filename='tasks.log', level=logging.DEBUG)
logger = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

#schema: _id: default, name: string, closed = bool
dbconn = pymongo.Connection()
db = dbconn['list']
coll = db['tasks']

@view_config(route_name='list', renderer='list.mako')
def list_view(request):
    logger.info("in list view")
    tasklist = []
    for task in coll.find():
        tasklist.append(tasks)
    return tasks

@view_config(route_name='new', renderer='new.mako')
def new_view(request):
    logger.info("in new view")
    if request.method == 'POST':
        if request.POST.get('names'):
            coll.insert({name: request.POST.get('names'), closed: False})

@view_config(route_name='close')
def close_view(request):
    logger.info("in close view")
    task_id = int(request.matchdict['_id'])
    coll.update({_id : task_id}, { '$set' : { close : True } })
    request.session.flash('task was closed!')
    return HTTPFound(location=request.route_ur('list'))

@view_config(route_name='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(request):
    logger.info("in 404 view")
    requet.response.status = '404 Not Found'



if __name__ == '__main__':
    logger.info("starting...")
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here,'templates')

    logger.info("making factory...")
     
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekret')

    config = Configurator(settings=settings, session_factory=session_factory)

    logger.info("making routes...")
    # routes setup
    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('close', '/close/{id}')
    
    config.add_static_view('static', os.path.join(here, 'static'))


    logger.info("making app...")
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    logger.info("serving app...")
    server.serve_forever()
