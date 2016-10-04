import pytest

from korben import config
from korben.cdms_api.rest.api import CDMSRestApi

@pytest.fixture(scope='session')
def cdms_client():
    'Placeholder for disconnect management and stuff?'
    client = CDMSRestApi()
    return client


@pytest.yield_fixture
def account_object(cdms_client):
    'Create an AccountSet object and delete it aferwards'
    create_resp = cdms_client.create('AccountSet', data={'Name': 'Timelort'})
    assert create_resp.ok
    acc = create_resp.json()['d']
    yield acc
    del_resp = cdms_client.delete(
        'AccountSet', "guid'{0}'".format(acc['AccountId'])
    )
    assert del_resp.ok
