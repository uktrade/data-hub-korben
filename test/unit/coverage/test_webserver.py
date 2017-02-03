import pytest
from unittest.mock import Mock

import importlib
import os

from cryptography.fernet import Fernet
import sqlalchemy as sqla
import redis

from korben import config
from korben.bau import webserver, sentry_client
from korben.cdms_api.rest import api
from korben.services import db


MOCK_DEFAULT_SETTINGS = {
    'odata_metadata': Mock,
    'django_metadata': Mock,
    'cdms_client': Mock,
}

@pytest.fixture
def mock_externals(monkeypatch):
    monkeypatch.setattr(webserver, 'DEFAULT_SETTINGS', MOCK_DEFAULT_SETTINGS)


def test_get_app_no_overrides(mock_externals):
    webserver.get_app()


def test_wsgi_app_constant(monkeypatch, mock_externals):
    monkeypatch.setattr(sentry_client, 'SENTRY_CLIENT', Mock())
    mock_get = Mock()
    mock_get.return_value = ''
    monkeypatch.setattr(os.environ, 'get', mock_get)
    temp_settings = {
        'cdms_base_url': 'a',
        'database_odata_url': 'HELLO MUM',
        'database_url': 'HELLO MUM',
        'cdms_username': 'd',
        'cdms_password': 'e',
        'cdms_base_url': 'f',
        'cdms_cookie_path': 'g',
        'cdms_cookie_key': Fernet.generate_key().decode('utf8'),
    }
    with config.temporarily(**temp_settings):
        try:
            importlib.reload(webserver)
        except redis.exceptions.ConnectionError as exc:
            assert 'Name or service not known' in str(exc)
        except sqla.exc.ArgumentError as exc:
            assert 'HELLO MUM' in str(exc)
