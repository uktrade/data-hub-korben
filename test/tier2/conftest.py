import pytest

from korben import config
from korben.etl import transform
from korben.cdms_api.rest.api import CDMSRestApi


def call_zorg(entity_type, guid):
    # queue a cdms object for deletion
    raise NotImplementedError()


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
    '''
    # this request takes a minute. fuck that
    del_resp = cdms_client.delete(
        'AccountSet', "guid'{0}'".format(acc['AccountId'])
    )
    assert del_resp.ok
    '''

@pytest.fixture(scope='session')
def django_advisor(cdms_client):
    # Little Mickey Hope
    resp = cdms_client.get(
        'SystemUserSet', "guid'07e3415a-9b98-e211-a939-e4115bead28a'"
    )
    assert resp.ok
    return transform.odata_to_django('SystemUserSet', resp.json()['d'])
