import datetime
import operator
import functools
import logging

import sqlalchemy as sqla

from korben import services
from korben.bau import leeloo
from korben.bau.views import fmt_guid
from korben.etl import transform, load, spec
from korben.sync.utils import select_chunks
from korben.sync.scrape import utils as scrape_utils, types
from korben.utils import entry_row

from korben.cdms_api.rest.api import CDMSRestApi

FMT_TRAVERSE_FLAG = '{0}/traverse/{1}'
LOGGER = logging.getLogger('korben.sync.traverse')


def process_response(target, response):
    'Return leeloo-ready dicts, write to odata database'
    short_cols = functools.partial(transform.colnames_longshort, target.name)
    long_cols = [
        spec.COLNAME_SHORTLONG.get((target.name, short_col), short_col)
        for short_col in map(operator.attrgetter('name'), target.columns)
    ]
    odata_dicts = []
    for cdms_dict in response.json()['d']['results']:
        odata_dicts.append(short_cols(entry_row(long_cols, cdms_dict)))
    load.to_sqla_table_idempotent(target, odata_dicts)
    retval = []
    for odata_dict in odata_dicts:
        retval.append(transform.odata_to_django(target.name, odata_dict))
    return retval


def cdms_pages(cdms_client, account_guid, odata_target, filters, offset):
    'Page through some request'
    response = cdms_client.list(odata_target.name, filters=filters)
    LOGGER.info(
        "%s %s took %ss", odata_target.name, offset, response.elapsed.seconds
    )
    try:
        scrape_utils.raise_on_cdms_resp_errors(
            odata_target.name, offset, response
        )
    except types.EntityPageNoData:
        return []
    django_dicts = process_response(odata_target, response)
    paging_done = len(django_dicts) < offset + 50
    while not paging_done:
        offset = offset + 50
        django_dicts.extend(
            cdms_pages(cdms_client, account_guid, odata_target, filters, offset)
        )
        paging_done = len(django_dicts) < offset
    return django_dicts


def cdms_to_leeloo(cdms_client, account_guid, odata_target, django_target, filters):
    redis_key = FMT_TRAVERSE_FLAG.format(django_target, account_guid)
    already_done = bool(services.redis.get(redis_key))
    if already_done:
        return []
    django_dicts = cdms_pages(cdms_client, account_guid, odata_target, filters, 0)
    LOGGER.info("Sending %s of %s to Leeloo", len(django_dicts), django_target)
    retval = leeloo.send(django_target, django_dicts)  # errors recorded here
    services.redis.set(redis_key, datetime.datetime.now().isoformat())
    LOGGER.info(
        "company_company %s -> %s traverse complete", account_guid, django_target
    )
    return retval


def traverse_from_account(cdms_client, odata_metadata, account_guid):
    'Query CDMS, downloading contacts and interactions for a given company'
    contact_responses = cdms_to_leeloo(
        cdms_client,
        account_guid,
        odata_metadata.tables['ContactSet'],
        'company_contact',
        "ParentCustomerId/Id eq {0}".format(fmt_guid(account_guid)),
    )
    interaction_responses = cdms_to_leeloo(
        cdms_client,
        account_guid,
        odata_metadata.tables['detica_interactionSet'],
        'company_interaction',
        "optevia_Organisation/Id eq {0}".format(fmt_guid(account_guid)),
    )


def main():
    '''
    Download everything, traversing from company to contact and then
    interaction. Tee the data to the OData database and Leeloo web API.
    '''
    cdms_client = CDMSRestApi()
    odata_metadata = services.db.get_odata_metadata()
    odata_table = odata_metadata.tables['AccountSet']
    base_select = sqla.select([odata_table])
    execute = odata_metadata.bind.execute
    odata_chunks = select_chunks(execute, odata_table, base_select)

    for odata_chunk in odata_chunks:
        for odata_row in odata_chunk:
            account_guid = getattr(odata_row, 'AccountId')
            traverse_from_account(
                cdms_client, odata_metadata, account_guid,
            )

if __name__ == '__main__':
    main()
