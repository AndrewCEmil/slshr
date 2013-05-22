from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

def hello_world(request):
    return Response('hello world...')

def basic_page(request):
    pagesrc = get_page_source()
    pagesrc.format(get_links())

def get_links():
    links = []
    links.append("http://google.com")
    links.append("http://bing.com")
    links.append("http://duckduckgo.com")
    return links

def get_page_source():
    return "<table><tr><td>Link: <a href=\"{0}\">Link0</a></td><td>Link: <a href=\"{1}\">Link1</a></td><td>Link: <a href=\"{2}\">Link2</a></td></tr></table>"

if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/hello')
    config.add_view(hello_world, route_name='hello')
    config.add_route('links', '/links')
    config.add_view(get_links, route_name='links')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
