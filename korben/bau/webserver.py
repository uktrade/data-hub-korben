import json

from wsgiref.simple_server import make_server
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid import httpexceptions as http_exc

from korben.cdms_api.rest import api
from korben.etl import spec, transform, utils
from korben.services import db


def json_exc_view(exc, request):
    'JSONify a Python exception, return it as a Response object'
    kwargs = {
        'status_code': exc.status_code,
        'body': json.dumps({'message': exc.message}),
        'content_type': 'application/json',
    }
    return Response(**kwargs)


def request_tablenames(request):
    'Extract table names from a request, raise things'
    django_tablename = request.matchdict['django_tablename']
    try:
        odata_tablename = spec.DJANGO_LOOKUP[django_tablename]
    except KeyError:
        message = "{0} is not mapped".format(django_tablename)
        raise http_exc.HTTPNotFound(message)
    return django_tablename, odata_tablename


def django_to_odata(request):
    'Transform request into spec for “onwards” request to OData service'
    django_tablename, odata_tablename = request_tablenames(request)
    try:
        etag, odata_dict = transform.django_to_odata(
            django_tablename, request.json_body
        )
    except json.JSONDecodeError as exc:
        raise http_exc.HTTPBadRequest('Invalid JSON')
    return odata_tablename, etag, odata_dict


def odata_to_django(odata_tablename, response):
    '''
    Transform an OData response into a response to pass on to Django (possibly
    just an “passed-through” error response)
    '''
    if not response.ok:
        kwargs = {
            'status_code': response.status_code,
            'body': json.dumps(response.json()),
            'content_type': 'application/json',
        }
        return Response(**kwargs)
    return transform.odata_to_django(odata_tablename, response.json()['d'])


@view_config(route_name='create', request_method=['POST'], renderer='json')
def create(request):
    'Create an OData entity'
    odata_tablename, _, odata_dict = django_to_odata(request)
    cdms_client = request.registry.settings['cdms_client']
    response = cdms_client.create(odata_tablename, odata_dict)
    return odata_to_django(odata_tablename, response)


@view_config(route_name='update', request_method=['POST'], renderer='json')
def update(request):
    'Update an OData entity'
    odata_tablename, etag, odata_dict = django_to_odata(request)
    odata_metadata = request.registry.settings['odata_metadata']
    odata_table = odata_metadata.tables[odata_tablename]
    ident = odata_dict.pop(utils.primary_key(odata_table), None)
    if ident is None:
        raise http_exc.HTTPBadRequest('No identifier provided; pass `id` key')
    cdms_client = request.registry.settings['cdms_client']
    response = cdms_client.update(odata_tablename, etag, ident, odata_dict)
    return odata_to_django(odata_tablename, response)


@view_config(route_name='get', request_method=['POST'], renderer='json')
def get(request):
    'Get an OData entity'
    django_tablename, odata_tablename = request_tablenames(request)
    ident = request.matchdict['ident']
    cdms_client = request.registry.settings['cdms_client']
    response = cdms_client.get(odata_tablename, ident)
    return odata_to_django(odata_tablename, response)


def get_app(overrides=None):
    settings = {
        'odata_metadata': db.get_odata_metadata(),
        'django_metadata': db.get_django_metadata(),
        'cdms_client': api.CDMSRestApi()
    }
    if overrides is not None:
        settings.update(overrides)
    app_cfg = Configurator(settings=settings)
    app_cfg.add_view(json_exc_view, context=http_exc.HTTPError)
    app_cfg.add_route('create', '/create/{django_tablename}')
    app_cfg.add_route('update', '/update/{django_tablename}')
    app_cfg.add_route('get', '/get/{django_tablename}/{ident}')
    app_cfg.scan()
    return app_cfg.make_wsgi_app()


def start():
    server = make_server('0.0.0.0', 8080, get_app())
    server.serve_forever()
