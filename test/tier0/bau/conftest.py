import pytest
from webtest import TestApp
from korben.bau import webserver
from korben.cdms_api.rest import api


@pytest.fixture
def test_app(monkeypatch, odata_test_service, tier0_postinitial):
    monkeypatch.setattr(api, 'CDMSRestApi', lambda: odata_test_service)
    app = webserver.get_app()
    return TestApp(app)
