import pytest

import re
import datetime
from korben.sync.utils import could_be_a_date_value


def test_delete_children(cdms_client):
    '''
    Demonstrate that some automatically created child objects are automatically
    deleted when the parent is deleted.
    '''
    create_resp = cdms_client.create('AccountSet', data={'Name': 'Sup Bae'})
    assert create_resp.ok
    account = create_resp.json()['d']

    address1_resp = cdms_client.get(
        'CustomerAddressSet', "guid'{0}'".format(account['Address1_AddressId'])
    )
    address1 = address1_resp.json()['d']
    assert address1['CustomerAddressId'] == account['Address1_AddressId']

    address2_resp = cdms_client.get(
        'CustomerAddressSet', "guid'{0}'".format(account['Address2_AddressId'])
    )
    address2 = address2_resp.json()['d']
    assert address2['CustomerAddressId'] == account['Address2_AddressId']

    del_resp = cdms_client.delete(
        'AccountSet', "guid'{0}'".format(account['AccountId'])
    )
    assert del_resp.ok

    address1_resp_404 = cdms_client.get(
        'CustomerAddressSet', "guid'{0}'".format(account['Address1_AddressId'])
    )
    assert address1_resp_404.status_code == 404

    address2_resp_404 = cdms_client.get(
        'CustomerAddressSet', "guid'{0}'".format(account['Address2_AddressId'])
    )
    assert address2_resp_404.status_code == 404


def test_time_fields(account_object):
    '''
    Demonstrate that time-related fields are populated automatically by
    Dynamics.
    '''
    fields = ['CreatedOn', 'ModifiedOn']
    for field in fields:
        # this will raise if there's not a date there
        datetime.datetime.strptime(
            could_be_a_date_value(account_object[field]), '%Y-%m-%d %H:%M:%S'
        )


def test_uuid_created(account_object):
    'Demonstrate that Dynamics creates something that looks like a UUID'
    match = re.match('.{8}-.{4}-.{4}-.{12}', account_object['AccountId'])
    # whole thing is matched
    assert match.span() == (0, 31)
