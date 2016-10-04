import pytest
from korben.bau import webserver
from webtest import TestApp


@pytest.fixture
def test_app():
    app = webserver.get_app()
    return TestApp(app)
