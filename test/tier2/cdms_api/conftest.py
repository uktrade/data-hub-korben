import tempfile
import pytest
import base64
import json
import os

from korben.cdms_api.rest.api import CDMSRestApi
from korben.cdms_api.rest.auth.active_directory import ActiveDirectoryAuth

def pytest_generate_tests(metafunc):
    'Grab user credentials from the environment'
    users_b64 = os.environ['CDMS_TEST_USERS']
    cdms_test_users = json.loads(base64.b64decode(users_b64).decode('utf-8'))
    metafunc.parametrize('credentials', cdms_test_users)


@pytest.yield_fixture
def cdms_client():
    'Create a new client for passed credentials'
    _, cookie_path = tempfile.mkstemp()
    def cdms_client_fn(username, password):
        auth = ActiveDirectoryAuth(
            username=username, password=password, cookie_path=cookie_path
        )
        return CDMSRestApi(auth=auth)
    yield cdms_client_fn
    try:
        os.remove(cookie_path)
    except FileNotFoundError:
        pass  # CookieStorage class deleted the file
