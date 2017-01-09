import json

from pyramid import httpexceptions as http_exc
from pyramid.response import Response

from korben.etl import spec, transform


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
            'charset': 'utf-8',
        }
        return Response(**kwargs)
    return transform.odata_to_django(odata_tablename, response.json()['d'])
