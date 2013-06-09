import os
import logging
import pymongo

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
`

from wsgiref.simple_server import make_server

logging.basicConfig()
logger = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

#schema: _id: default, name: string, closed = bool
dbconn = pymongo.Connection()
db = dbconn['list']
coll = db['tasks']

@view_config(route_name='list', renderer='list.mako')
def list_view(request):
    tasklist = []
    for task in coll.find():
        tasklist.append(tasks)
    return tasks

@view_config(route_name='new', renderer='new.mako')
def new_view(request):
    if request.method == 'POST':
        if request.POST.get('names'):
            coll.insert({name: request.POST.get('names'), closed = False})

@view_config(route_name='close')
def close_view(request):
    task_id = int(request.matchdict['_id'])
    coll.update({_id : task_id}, { '$set' : { close : True } })
    request.session.flash('task was closed!')
    return HTTPFound(location=request.route_ur('list'))

@view_config(route_name='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(request):
    requet.response.status = '404 Not Found'



if __name__ == '__main__':
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True

    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekret')

    config = Configurator(settings=settings, session_factory=session_factory)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
