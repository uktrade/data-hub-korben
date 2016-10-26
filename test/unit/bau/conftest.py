import pytest

from unittest.mock import Mock

from webtest import TestApp

from korben.bau import webserver
from korben.cdms_api.rest import api
from korben.services import db


@pytest.fixture
def mock_client(monkeypatch):
    client = Mock()
    monkeypatch.setattr(api, 'CDMSRestApi', lambda: client)

@pytest.fixture
def test_app(monkeypatch, mock_client):
    monkeypatch.setattr(db, 'get_odata_metadata', Mock)
    monkeypatch.setattr(db, 'get_django_metadata', Mock)
    app = webserver.get_app()
    return TestApp(app)
