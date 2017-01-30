import pytest

from unittest.mock import Mock, call

import functools
import json

import requests

from korben import config
from korben import services
from korben.bau import leeloo


DJANGO_TABLENAME = 'cakes'
DJANGO_DICT = {'flavour': 'yum', 'fat': 'yes'}


def test_construct_request(monkeypatch):
    monkeypatch.setattr(config, 'datahub_secret', b'apples')
    prepared_request = leeloo.construct_request(DJANGO_TABLENAME, DJANGO_DICT)
    assert len(prepared_request.headers['X-Signature'])
    assert prepared_request.headers['Content-Type'] == 'application/json'
    assert json.loads(prepared_request.body.decode('utf-8')) == DJANGO_DICT
    assert prepared_request.path_url == "/korben/{0}/".format(DJANGO_TABLENAME)


@pytest.fixture
def mock_session(monkeypatch):
    monkeypatch.setattr(config, 'datahub_secret', b'oranges')
    mock_session_class = Mock()
    mock_session_instance = Mock()
    mock_session_class.return_value = mock_session_instance
    monkeypatch.setattr(requests, 'Session', mock_session_class)
    return mock_session_instance

AN_GUID = 'abc'

def mock_send_method(ok, status_code, _):
    mock_response = Mock()
    mock_response.ok = ok
    mock_response.status_code = status_code
    mock_response.request.body = bytes(
        '{{"id": "{0}"}}'.format(AN_GUID), 'utf-8'
    )
    return mock_response

def test_send_success(monkeypatch, mock_session):
    'Assert the Redis instance didn’t get called when Leeloo responses were OK'
    mock_redis = Mock()
    monkeypatch.setattr(services, 'redis', mock_redis)
    mock_session.send = functools.partial(mock_send_method, True, 200)
    send_retval = leeloo.send(DJANGO_TABLENAME, [DJANGO_DICT])
    assert mock_redis.call_count == 0


def test_send_failure(monkeypatch, mock_session):
    'Assert the Redis got called when Leeloo responses were not OK'
    mock_redis = Mock()
    monkeypatch.setattr(services, 'redis', mock_redis)
    mock_session.send = functools.partial(mock_send_method, False, 418)
    send_retval = leeloo.send(DJANGO_TABLENAME, [DJANGO_DICT, DJANGO_DICT])
    mock_redis.set.assert_has_calls([call('cakes/fail/abc', 418)] * 2)
