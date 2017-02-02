import pytest

from unittest.mock import Mock

from webtest import TestApp

from korben.bau import webserver
from korben.bau import sentry_client
from korben.cdms_api.rest import api
from korben.services import db


@pytest.fixture
def test_app(monkeypatch):
    monkeypatch.setattr(db, 'get_odata_metadata', Mock)
    monkeypatch.setattr(db, 'get_django_metadata', Mock)
    monkeypatch.setattr(sentry_client, 'SENTRY_CLIENT', Mock())
    app = webserver.get_app({'cdms_client': Mock()})
    return TestApp(app)
