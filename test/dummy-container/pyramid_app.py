import collections
import json
import os
import uuid

import yaml
from pyramid import httpexceptions as http_exc
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from wsgiref.simple_server import make_server

DJANGO_TABLENAMES = {
    'company_company',
    'company_advisor',
    'company_contact',
    'company_interaction',
}

DJANGO_FIXTURES = collections.defaultdict(dict)
with open('django_fixtures.yaml', 'r') as yaml_fh:
    for django_fixture in yaml.load(yaml_fh):
        tablename = django_fixture['model'].replace('.', '_')
        ident = django_fixture.get('pk') or django_fixture['id']
        django_fixture['fields'].update({'id': ident})
        DJANGO_FIXTURES[tablename][ident] = django_fixture['fields']

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


@view_config(route_name='get', request_method=['GET'], renderer='json')
def get(request):
    tablename = validate_tablename(request)
    ident = request.matchdict['ident']
    result = DJANGO_FIXTURES.get(tablename, {}).get(ident)
    if not result:
        return (tablename, ident)
        message = "Fixture for {0} with id {1} not found".format(
            tablename, ident
        )
        raise http_exc.HTTPNotFound(message)
    return result


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
    server = make_server('0.0.0.0', 8080, get_app())
    server.serve_forever()
