import pytest

import sqlalchemy as sqla

from korben.services import db
from korben.bau import poll


@pytest.mark.skipif(True, reason='Don’t control staging')
def test_poll(cdms_client, account_object):
    'Test poll picks up changes to newer objects'
    new_name = 'Magic account'
    # one poll call to get the newest 50
    poller = poll.CDMSPoller(client=cdms_client)
    poller.poll_entities(['AccountSet'])
    # set up our query
    django_metadata = db.get_django_metadata()
    table = django_metadata.tables['company_company']
    select_statement = (
        sqla.select([table.c.name], table)
            .where(table.c.id == account_object['AccountId'])
    )
    django_name = django_metadata.bind.execute(select_statement).scalar()
    assert django_name == account_object['Name']
    # change the company name
    update_resp = cdms_client.update(
        'AccountSet',
        "guid'{0}'".format(account_object['AccountId']),
        {'Name': new_name},
    )
    assert update_resp.ok
    # the below poops rows into the django database
    poller.poll_entities(['AccountSet'])
    django_name_now = django_metadata.bind.execute(select_statement).scalar()
    assert django_name_now == new_name
