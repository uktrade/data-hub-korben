import collections
import json
import logging
import os
import uuid

import yaml
from pyramid import httpexceptions as http_exc
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from wsgiref.simple_server import make_server

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('dummy-korben')
DJANGO_TABLENAMES = {
    'company_company',
    'company_advisor',
    'company_contact',
    'company_interaction',
}


@view_config(context=Exception)
def json_exc_view(exc, _):
    kwargs = {
        'status_code': 500,
        'body': json.dumps({'message': str(exc)}),
        'content_type': 'application/json',
    }
    return Response(**kwargs)


@view_config(context=http_exc.HTTPError)
def json_http_exc_view(exc, _):
    'JSONify a Python exception, return it as a Response object'
    LOGGER.error(exc.message)
    kwargs = {
        'status_code': exc.status_code,
        'body': json.dumps({'message': exc.message}),
        'content_type': 'application/json',
    }
    return Response(**kwargs)


def validate_tablename(request):
    django_tablename = request.matchdict['django_tablename']
    if django_tablename in DJANGO_TABLENAMES:
        return django_tablename
    message = "{0} is not mapped".format(django_tablename)
    raise http_exc.HTTPNotFound(message)


@view_config(route_name='create', request_method=['POST'], renderer='json')
def create(request):
    validate_tablename(request)
    resp_dict = request.json_body
    resp_dict['id'] = str(uuid.uuid4())
    return resp_dict


@view_config(route_name='update', request_method=['POST'], renderer='json')
def update(request):
    validate_tablename(request)
    return request.json_body


@view_config(route_name='get', request_method=['POST'], renderer='json')
def get(request):
    validate_tablename(request)
    return request.json_body


def get_app(settings=None):
    if settings is None:
        settings = {}
    app_cfg = Configurator(settings=settings)
    app_cfg.add_route('create', '/create/{django_tablename}')
    app_cfg.add_route('update', '/update/{django_tablename}')
    app_cfg.add_route('get', '/get/{django_tablename}/{ident}')
    app_cfg.scan()
    return app_cfg.make_wsgi_app()


if __name__ == '__main__':
    LOGGER.info('Starting dummy korben bau')
    server = make_server('0.0.0.0', 8080, get_app())
    server.serve_forever()
