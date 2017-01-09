import json
import logging

import yaml
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid import httpexceptions as http_exc
from wsgiref.simple_server import make_server

from korben import etl
from huey_config import huey_instance
from huey_tasks import delete_odata

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('korben-tier2-deleter')


@view_config(context=Exception)
def json_exc_view(exc, _):
    kwargs = {
        'status_code': 500,
        'body': json.dumps({'message': str(exc)}),
        'content_type': 'application/json',
        'charset': 'utf-8',
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
        'charset': 'utf-8',
    }
    return Response(**kwargs)


def tablename_django_to_odata(django_tablename):
    if django_tablename in etl.spec.DJANGO_LOOKUP:
        return django_tablename
    message = "{0} is not mapped".format(django_tablename)
    raise http_exc.HTTPNotFound(message)


@view_config(
    route_name='delete-django', request_method=['GET'], renderer='json'
)
def delete_django(request):
    django_tablename = request.matchdict['django_tablename']
    odata_tablename = tablename_django_to_odata(django_tablename)
    ident = request.matchdict['ident']
    result = delete_odata(odata_tablename, ident)
    LOGGER.info(
        'Deleting %s with ident %s (%s)',
        django_tablename, ident, result.task.task_id
    )
    return {
        'django_tablename': django_tablename,
        'ident': ident,
        'result_id': result.task.task_id,
    }


def get_app(settings=None):
    if settings is None:
        settings = {}
    app_cfg = Configurator(settings=settings)
    app_cfg.add_route('delete-django', '/delete/django/{django_tablename}/{ident}')
    app_cfg.scan()
    return app_cfg.make_wsgi_app()


if __name__ == '__main__':
    LOGGER.info('Starting korben deleter service')
    SERVER = make_server('0.0.0.0', 8090, get_app())
    SERVER.serve_forever()
