import asyncio
from math import ceil
from urllib.parse import urlencode

from aiohttp import web
from jinja2 import Environment
from jinja2 import FileSystemLoader
from raven import Client
client = Client()

from search import search_gifs


class Paginator(object):
    def __init__(self, request, objs, page, per_page=20):
        self.request = request
        self.objs = objs
        self.total_count = len(objs)
        self.page = page
        self.start = (page - 1) * per_page
        self.end = self.start + per_page
        self.pages = int(ceil(self.total_count / float(per_page)))
        self.has_next = self.page < self.pages
        self.has_prev = self.page > 1
        self.has_pages = self.pages > 1

    def url(self, page):
        params = dict(self.request.GET.items(getall=True))
        params['page'] = page
        query_string = urlencode(list(params.items()))
        return '{}?{}'.format(self.request.path, query_string)

    def page_iter(self):
        return range(1, self.pages + 1)

    def __iter__(self):
        for obj in self.objs[self.start:self.end]:
            yield obj


def get_db(year):
    return 'DB{}'.format(int(year) - 2006)


def render(request, template, headers=None, encoding='utf-8', status=200,
           **context):
    try:
        template = request.app.jinja.get_template(template)
        context['request'] = request
        output = template.render(webapp=request.app, **context)
        body = output.encode(encoding)
        headers = headers or {
            'Content-Type': 'text/html',
        }
        headers['Content-Length'] = str(len(body))
        response = web.Response(request, body, status=status, headers=headers)
        return response
    except:
        client.captureException()
        raise


def render_list(request, title, gifs, status=200):
    gifs = Paginator(
        request=request,
        objs=gifs,
        page=int(request.GET.get('page', 1))
    )
    return render(
        request,
        'list.html',
        gifs=gifs,
        title=title,
        db=request.app.db,
        status=status
    )


@asyncio.coroutine
def index_view(request):
    return render_list(request, "Index", request.app.db.gifs)


@asyncio.coroutine
def person_view(request):
    name = request.match_info['name']
    try:
        gifs = request.app.db.people[name]
    except KeyError:
        return four_oh_four(request)
    return render_list(request, name.capitalize(), gifs)


@asyncio.coroutine
def year_view(request):
    year = int(request.match_info['year'])
    try:
        gifs = request.app.db.years[year]
        desertbus = get_db(year)
    except KeyError:
        return four_oh_four(request)
    return render_list(request, desertbus, gifs)


@asyncio.coroutine
def search_view(request):
    term = request.GET.get('q', '')
    results = search_gifs(request.app.db, term)
    title = 'Results: {}'.format(term)
    return render_list(request, title, results)


@asyncio.coroutine
def four_oh_four(request):
    return render_list(request, 'Not Found', [], request.app.db, status=404)


@asyncio.coroutine
def osd_view(request):
    return render(
        request,
        'opensearchdescription.xml',
        headers={
            'Content-Type': 'text/xml',
        }
    )


def build_web_app(config, database):
    webapp = web.Application()
    webapp.db = database
    webapp.jinja = Environment(loader=FileSystemLoader(config.templates_dir))
    webapp.router.add_route('GET', '/', index_view)
    webapp.router.add_route('GET', '/c/{name}/', person_view)
    webapp.router.add_route('GET', '/y/{year}/', year_view)
    webapp.router.add_route('GET', '/s/', search_view)
    webapp.router.add_route('GET', '/opensearchdescription.xml', osd_view)
    webapp.router.add_static('/static/', config.static_dir)
    webapp.router.add_static('/gifs/', config.gifs_dir)
    return webapp
