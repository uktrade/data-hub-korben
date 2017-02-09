import pytest

from unittest.mock import Mock

from webtest import TestApp

from korben.bau import webserver
from korben.bau import sentry_client
from korben.cdms_api.rest import api
from korben.services import db


@pytest.fixture
def mock_client(monkeypatch):
    client = Mock()
    monkeypatch.setattr(api, 'CDMSRestApi', lambda: client)


@pytest.fixture
def mock_externals(monkeypatch):
    monkeypatch.setattr(sentry_client, 'SENTRY_CLIENT', Mock())


@pytest.fixture
def test_app(mock_externals, mock_client):
    app = webserver.get_app({
        'odata_metadata': Mock,
        'django_metadata': Mock,
        'cdms_client': Mock,
    })
    return TestApp(app)
