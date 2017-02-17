'Report status of attached services'
import sqlalchemy as sqla
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.security import NO_PERMISSION_REQUIRED

from korben import services
from korben.cdms_api.rest import api as cdms_api
from .poll import HEARTBEAT


def database():
    try:
        metadata = services.db.get_odata_metadata()
        assert isinstance(metadata, sqla.MetaData)
    except Exception as exc:
        return False, str(exc)
    return True, None


def redis():
    try:
        services.redis.info()
    except Exception as exc:
        return False, str(exc)
    return True, None


def cdms():
    try:
        cdms_client = cdms_api.CDMSRestApi()
        cdms_response = cdms_client.list('AccountSet')
        status = cdms_response.status_code
        if status != 200:
            return False, "CDMS replied with {0}".format(status)
    except Exception as exc:
        return False, str(exc)
    return True, None


def polling():
    try:
        heartbeat = services.redis.get(HEARTBEAT)
        if not heartbeat:  # that’s bad, right?
            return False, 'Heartbeat was found to be missing'
    except Exception as exc:
        return False, str(exc)
    return True, None


status_functions = (database, redis, cdms, polling)

PINGDOM_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>{0}</status>
</pingdom_http_custom_check>\n'''

COMMENT_TEMPLATE = '<!--{0}-->\n'


@view_config(route_name='status', permission=NO_PERMISSION_REQUIRED)
def pingdom(request):
    'Return some Pingdom formatted XML describing status of attached systems'
    failures = []
    for status_function in status_functions:
        success, reason = status_function()
        if not success:
            failures.append(
                "{0} failed because '{1}'".format(
                    status_function.__name__, reason or '???'
                )
            )
    status_code, status_msg = (500, 'FALSE') if any(failures) else (200, 'OK')
    body = PINGDOM_TEMPLATE.format(status_msg)
    for message in failures:
        body += COMMENT_TEMPLATE.format(message)
    response_kwargs = {
        'status_code': status_code,
        'body': body,
        'content_type': 'text/xml',
        'charset': 'utf-8',
    }
    return Response(**response_kwargs)
