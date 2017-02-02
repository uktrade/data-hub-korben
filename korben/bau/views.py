import json
import logging
import uuid

from pyramid import httpexceptions as http_exc
from pyramid.response import Response
from pyramid.view import view_config
from requests.exceptions import RequestException

from korben.cdms_api.rest.api import CDMSRestApi
from korben.cdms_api.rest.auth.active_directory import ActiveDirectoryAuth
from korben.etl import utils as etl_utils

from . import common
from .sentry_client import SENTRY_CLIENT

LOGGER = logging.getLogger('korben.bau.views')


def fmt_guid(ident):
    'Format some string as a Dynamics GUID'
    return "guid'{0}'".format(ident)


@view_config(context=Exception)
def json_exc_view(exc, _):
    'Generic view to log and return exceptions'
    SENTRY_CLIENT.captureException()
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


@view_config(route_name='create', request_method=['POST'], renderer='json')
def create(request):
    'Create an OData entity'
    odata_tablename, _, odata_dict = common.django_to_odata(request)
    cdms_client = request.registry.settings['cdms_client']
    response = cdms_client.create(odata_tablename, odata_dict)
    return common.odata_to_django(odata_tablename, response)


@view_config(route_name='update', request_method=['POST'], renderer='json')
def update(request):
    'Update an OData entity'
    odata_tablename, etag, odata_dict = common.django_to_odata(request)
    odata_metadata = request.registry.settings['odata_metadata']
    odata_table = odata_metadata.tables[odata_tablename]
    ident = odata_dict.pop(etl_utils.primary_key(odata_table), None)
    if ident is None:
        raise http_exc.HTTPBadRequest('No identifier provided; pass `id` key')
    cdms_client = request.registry.settings['cdms_client']
    response = cdms_client.update(
        odata_tablename, etag, fmt_guid(ident), odata_dict
    )
    return common.odata_to_django(odata_tablename, response)


@view_config(route_name='get', request_method=['POST'], renderer='json')
def get(request):
    'Get an OData entity'
    _, odata_tablename = common.request_tablenames(request)
    ident = request.matchdict['ident']
    cdms_client = request.registry.settings['cdms_client']
    response = cdms_client.get(odata_tablename, fmt_guid(ident))
    return common.odata_to_django(odata_tablename, response)


@view_config(
    route_name='validate-credentials',
    request_method=['POST'],
    renderer='json'
)
def validate_credentials(request):
    'Validate a set of CDMS credentials'
    cdms_cookie_path = uuid.uuid4().hex
    try:
        json_data = request.json_body
        username = json_data.get('username')
        password = json_data.get('password')

        if not (username and password):
            SENTRY_CLIENT.captureMessage(
                'Missing credentials from validate-credentials request body'
            )
            return False
        auth = ActiveDirectoryAuth(username, password, cdms_cookie_path)
        api_client = CDMSRestApi(auth)
        api_client.auth.login()
    except (ValueError, RequestException):
        SENTRY_CLIENT.captureException()
        return False
    return True
