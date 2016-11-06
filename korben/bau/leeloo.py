import json
import logging


from korben import config
from korben.utils import generate_signature

import requests


LOGGER = logging.getLogger('korben.bau.leeloo')


def construct_request(django_tablename, django_dict):
    'Construct a signed request'
    unprepared_request = requests.Request(
        method='POST',
        url="{0}/{1}/".format(config.leeloo_url, django_tablename),
        json=django_dict,
        headers={'Content-Type': 'application/json'},
    )
    prepared_request = unprepared_request.prepare()
    signature = generate_signature(
        bytes(prepared_request.path_url, 'utf-8'),
        prepared_request.body,
        config.datahub_secret
    )
    prepared_request.headers['X-Signature'] = signature
    return prepared_request


def send(django_tablename, django_dicts):
    'Send objects to leeloo'
    session = requests.Session()
    responses = []
    for django_dict in django_dicts:
        request = construct_request(django_tablename, django_dict)
        responses.append(session.send(request))
    if not all([response.ok for response in responses]):
        LOGGER.error('The following requests failed:')
        for response in responses:
            if not response.ok:
                LOGGER.error(
                    '    %s %s %s',
                    response.status_code,
                    response.request.path_url,
                    json.loads(response.request.body.decode('utf-8'))['id']
                )
    return responses
