from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

def hello_world(request):
    return Response('hello world...')

def basic_page(request):
    links = get_links()
    pagesrc = get_page_source(len(links))
    return Response(pagesrc.format(links[0], links[1], links[2]))

def get_links():
    links = []
    links.append("http://google.com")
    links.append("http://bing.com")
    links.append("http://duckduckgo.com")
    return links

def get_page_source(linkcount):
    elementhtml = "<tr><td>Link: <a href=\"{0}\">Link{1}</a></tr></td>"
    fullhtml = "<table>"
    for i in range(linkcount):
        fullhtml = fullhtml + elementhtml.format("{" + str(i) + "}", i)
    fullhtml += "</table>"
    return fullhtml

if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/hello')
    config.add_view(hello_world, route_name='hello')
    config.add_route('links', '/links')
    config.add_view(basic_page, route_name='links')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
