import json
from wsgiref.simple_server import make_server
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid import httpexceptions as http_exc


from korben.etl import spec


def json_exception(exc, request):
    return Response(
        status_code=exc.status_code,
        body=json.dumps({'message': exc.message}),
        content_type='application/json',
    )

def get_odata_tablename(request):
    django_tablename = request.matchdict['django_tablename']
    try:
        return spec.DJANGO_LOOKUP[django_tablename]
    except KeyError:
        message = "{0} is not mapped".format(django_tablename)
        raise http_exc.HTTPNotFound(message)

@view_config(request_method=['POST'])
def create(request):
    odata_tablename = get_odata_tablename(request)


@view_config(request_method=['POST'])
def update(request):
    django_tablename = request.matchdict['django_tablename']


def start():
    config = Configurator()
    config.add_view(
        json_exception, context=http_exc.HTTPError, renderer='json'
    )
    config.add_route('create', '/create/{django_tablename}')
    config.add_route('update', '/update/{django_tablename}')
    config.add_view(create, route_name='create')
    config.add_view(update, route_name='update')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()