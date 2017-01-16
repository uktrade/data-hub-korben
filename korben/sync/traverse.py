import operator
import functools
import logging

import sqlalchemy as sqla

from korben import services
from korben.bau import leeloo
from korben.bau.views import fmt_guid
from korben.etl import transform, load
from korben.sync.utils import select_chunks
from korben.utils import entry_row

from korben.cdms_api.rest.api import CDMSRestApi

client = CDMSRestApi()
LOGGER = logging.getLogger('korben.sync.traversal_fill')


def process_response(target, response):
    'Return leeloo-ready dicts, write to odata database'
    short_cols = functools.partial(transform.colnames_longshort, target.name)
    long_cols = [
        COLNAME_SHORTLONG.get((target.name, short_col), short_col)
        for short_col in map(operator.attrgetter('name'), target.columns)
    ]
    odata_dicts = []
    for cdms_dict in response.json()['d']['results']:
        odata_dicts.append(short_cols(utils.entry_row(long_cols, cdms_dict)))
    load.to_sqla_table_idempotent(target, odata_rows)
    retval = []
    for odata_dict in odata_dicts:
        retval.append({
            left: str(right) for left, right in
            transform.odata_to_django(target.name, odata_dict).items()
        })
    return retval


def cdms_to_leeloo(account_guid, odata_target, django_target, filters):
    response = client.list(odata_target.name, filters=filters)
    assert response.ok
    django_dicts = process_response(odata_target, response)
    return leeloo.send(django_target, django_dicts)


def traverse_from_account(odata_metadata, django_metadata, account_guid):
    'Query CDMS, downloading contacts and interactions for a given company'

    contact_responses = cdms_to_leeloo(
        odata_metadata.tables['ContactSet'],
        'company_contact',
        "ParentCustomerId/Id eq {0}".format(fmt_guid(account_guid)),
    )

    interaction_responses = cdms_to_leeloo(
        odata_metadata.tables['detica_interactionSet'],
        'company_interaction',
        "optevia_Organisation/Id eq {0}".format(fmt_guid(account_guid)),
    )

    '''
    django_dict = {
        k: str(v) for k, v in
        transform.odata_to_django('company_contact', dict(odata_row)).items()
    }
    response = leeloo.send(django_tablename, [django_dict])[0]
    if response.status_code != 200:
        services.redis.set(
            failure_fmt.format(getattr(odata_row, odata_pkey)),
            response.content.decode(response.encoding)
        )
    print("{0} already existed, {1} sent, {2} failed".format(skipped, sent, failed))
    '''


def main():
    '''
        (
            'ContactSet',
            'ContactId',
            'company_contact',
            'contact-failures/{0}'
        ),
        (
            'detica_interactionSet',
            'ActivityId',
            'company_interaction',
            'interaction-failures/{0}'
        ),
    traversal = (
        (
            'AccountSet',
            'AccountId',
            'company_company',
            'company-failures/{0}',
            None
        ),
    )
    for step in traversal:
        sync(*step)
    get company guid
    list contacts, filtering on copmany guid
    list interactions, filtering on copmany guid
    download all the contacts (pagination?)
    send all the contacts that aren't already held in django
    record 'contact-failures/{guid}' if something fails
    hit the interactions link
    download all the interactions (pagination?)
    send all interactions that aren't held in django
    record 'interaction-failures/{guid}' for failures
    '''
    # odata_tablename, odata_pkey, django_tablename, failure_fmt, traversal_key
    LOGGER.info("{0} -> {1}".format(odata_tablename, django_tablename))
    odata_metadata = services.db.get_odata_metadata()
    odata_table = odata_metadata.tables['detica_interactionSet']
    django_table = django_metadata.tables['company_company']
    django_metadata = services.db.get_django_metadata()
    odata_chunks = select_chunks(
        odata_metadata.bind.execute,
        odata_table,
        sqla.select([odata_table])
    )

    for odata_chunk in odata_chunks:
        for odata_row in odata_chunk:
            account_guid = getattr(odata_row, 'AccountId')
            comparitor = django_table.c.id == account_guid
            select = sqla.select([django_table]).where(comparitor)
            result = django_metadata.bind.execute(select).fetchone()
            traverse(odata_metadata, django_metadata, account_guid)

if __name__ == '__main__':
    main()
