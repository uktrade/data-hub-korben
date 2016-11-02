import json

from pyramid import httpexceptions as http_exc
from pyramid.response import Response
from pyramid.view import view_config

from korben.etl import utils as etl_utils
from . import common

def fmt_guid(ident):
    return "guid'{0}'".format(ident)

def json_exc_view(exc, request):
    'JSONify a Python exception, return it as a Response object'
    kwargs = {
        'status_code': exc.status_code,
        'body': json.dumps({'message': exc.message}),
        'content_type': 'application/json',
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
    django_tablename, odata_tablename = common.request_tablenames(request)
    ident = request.matchdict['ident']
    cdms_client = request.registry.settings['cdms_client']
    response = cdms_client.get(odata_tablename, fmt_guid(ident))
    return common.odata_to_django(odata_tablename, response)
