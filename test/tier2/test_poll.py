import pytest

import sqlalchemy as sqla

from korben import config
from korben.services import db
from korben.sync.poll import poll


@pytest.mark.skipif(True, reason='Don’t control staging')
def test_poll(cdms_client, account_object):
    'Test poll picks up changes to newer objects'
    new_name = 'Magic account'
    # one poll call to get the newest 50
    poll(cdms_client, entities=['AccountSet'])
    # set up our query
    django_metadata = db.poll_for_metadata(config.database_url)
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
    poll(cdms_client, entities=['AccountSet'])
    django_name_now = django_metadata.bind.execute(select_statement).scalar()
    assert django_name_now == new_name
