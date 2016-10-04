import json

from wsgiref.simple_server import make_server
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid import httpexceptions as http_exc

from korben import config
from korben.cdms_api.rest import api
from korben.etl import spec, transform
from korben.services import db


def json_exc_view(exc, request):
    kwargs = {
        'status_code': exc.status_code,
        'body': json.dumps({'message': exc.message}),
        'content_type': 'application/json',
    }
    return Response(**kwargs)


def django_to_odata(request):
    django_tablename = request.matchdict['django_tablename']
    try:
        odata_tablename = spec.DJANGO_LOOKUP[django_tablename]
    except KeyError:
        message = "{0} is not mapped".format(django_tablename)
        raise http_exc.HTTPNotFound(message)
    odata_metadata = request.registry.settings['odata_metadata']
    odata_table = odata_metadata.tables[odata_tablename]
    try:
        odata_dict = transform.django_to_odata(request.json_body)
    except json.decoder.JSONDecodeError as exc:
        raise http_exc.HTTPBadRequest('Invalid JSON')
    return odata_table, odata_dict


@view_config(request_method=['POST'])
def create(request):
    odata_table, odata_dict = django_to_odata(request)
    cdms_client = request.registry.settings['cdms_client']
    resp = cdms_client.create(odata_table.name, odata_dict)

@view_config(request_method=['POST'])
def update(request):
    odata_table, odata_dict = django_to_odata(request)
    cdms_client = request.registry.settings['cdms_client']
    resp = cdms_client.update(odata_table.name, odata_dict)


def get_app(overrides=None):
    settings = {
        'odata_metadata': db.poll_for_metadata(config.database_odata_url),
        'django_metadata': db.poll_for_metadata(config.database_url),
        'cdms_client': api.CDMSRestApi()
    }
    if overrides is not None:
        settings.update(overrides)
    app_cfg = Configurator(settings=settings)
    app_cfg.add_view(json_exc_view, context=http_exc.HTTPError)
    app_cfg.add_route('create', '/create/{django_tablename}')
    app_cfg.add_route('update', '/update/{django_tablename}')
    app_cfg.add_view(create, route_name='create')
    app_cfg.add_view(update, route_name='update')
    return app_cfg.make_wsgi_app()

def start():
    server = make_server('0.0.0.0', 8080, get_app())
    server.serve_forever()
