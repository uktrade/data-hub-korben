import pytest
from webtest import TestApp
from korben.bau import webserver
from korben.cdms_api.rest import api


@pytest.fixture
def test_app():
    app = webserver.get_app()
    return TestApp(app)
