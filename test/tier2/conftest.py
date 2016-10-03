import pytest

from korben import config
from korben.cdms_api.rest.api import CDMSRestApi

@pytest.fixture(scope='session')
def cdms_client():
    client = CDMSRestApi()
    return client

@pytest.fixture(scope='session')
def staging_fixtures(cdms_client):
    import ipdb;ipdb.set_trace()
    # create
    yield
