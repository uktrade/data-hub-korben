import pytest
from unittest.mock import Mock

import importlib
import os

import sqlalchemy as sqla

from korben import config
from korben.bau import webserver
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


def test_wsgi_app_constant(monkeypatch):
    mock_get = Mock()
    mock_get.return_value = ''
    monkeypatch.setattr(os.environ, 'get', mock_get)
    setattr(config, 'cdms_base_url', '')
    setattr(config, 'database_odata_url', 'HELLO MUM')
    try:
        importlib.reload(webserver)
    except sqla.exc.ArgumentError as exc:
        assert 'HELLO MUM' in str(exc)
