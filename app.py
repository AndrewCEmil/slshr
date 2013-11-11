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
from pyramid.authentication import SessionAuthenticationPolicy

from wsgiref.simple_server import make_server

logging.basicConfig(filename=__file__+'.log', level=logging.DEBUG)
logger = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

def main():
    logger.info("inside main, starting up")
    settings = get_settings()
    session_factory = get_session_factory()
    authn_policy = SessionAuthenticationPolicy()
    config = Configurator(settings=settings, session_factory=session_factory,
                          authentication_policy=authn_policy)
    add_routes(config)
    config.scan(package="tasks")
    app = config.make_wsgi_app()
    logger.info("about to start serving")
    serve(app)

def serve(app):
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

def get_settings():
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here, 'templates')
    return settings

def get_session_factory():
    return UnencryptedCookieSessionFactoryConfig('itsaseekreet')

#note: includes static view setup
def add_routes(config):
    config.add_route('home', '/')
    config.add_route('playlists', '/people')
    config.add_route('playlist', '/playlist/{name}')
    config.add_route('feed', '/feed/{name}')
    config.add_route('newuser', '/newuser')
    config.add_route('edit', '/edit')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('followers', '/followers/{followee}')
    config.add_route('following', '/following/{follower}')
    config.add_route('followreq', '/follow')
    config.add_route('unfollowreq', '/unfollow')
    config.add_route('deleteid', '/deleteid')
    config.add_route('deleteidx', '/deleteidx')
    config.add_static_view('static', os.path.join(here, 'static'))
    
if __name__ == '__main__':
    main()
