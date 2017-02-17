import datetime
import functools
import logging
import operator
import time

import sqlalchemy as sqla

from korben import services
from korben.bau import leeloo
from korben.bau.poll import POLL_SLEEP
from korben.bau import views
from korben.etl import transform, load, spec
from korben.sync.scrape import utils as scrape_utils, types
from korben.sync.utils import select_chunks
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
    try:
        entries = response.json()['d']['results']
    except TypeError:  # handle non-cdms case
        entries = response.json()['d']
    odata_dicts = []
    for cdms_dict in entries:
        odata_dicts.append(short_cols(entry_row(long_cols, cdms_dict)))
    load.to_sqla_table_idempotent(target, odata_dicts)
    retval = []
    for odata_dict in odata_dicts:
        retval.append(transform.odata_to_django(target.name, odata_dict))
    return retval


def cdms_pages(client, guid, odata_target, filters, offset):
    'Page through some request'
    response = client.list(odata_target.name, filters=filters, skip=offset)
    if response.elapsed.seconds > 5:
        LOGGER.info(
            "%s ! %s (%s) %ss",
            guid, odata_target.name, offset, response.elapsed.seconds
        )
    try:
        scrape_utils.raise_on_cdms_resp_errors(
            odata_target.name, offset, response
        )
    except types.EntityPageNoData:  # particular case, pass
        return []
    except types.EntityPageException:  # general case, retry
        time.sleep(POLL_SLEEP)
        LOGGER.info('%s -> %s failed', guid, odata_target.name)
        return cdms_pages(client, guid, odata_target, filters, offset)
    django_dicts = process_response(odata_target, response)
    if not django_dicts:
        return django_dicts
    paging_done = len(django_dicts) < offset + 50
    while not paging_done:
        offset = offset + 50
        django_dicts.extend(
            cdms_pages(client, guid, odata_target, filters, offset)
        )
        paging_done = len(django_dicts) < offset
    return django_dicts


def cdms_to_leeloo(client, guid, odata_target, django_target, filters):
    redis_key = FMT_TRAVERSE_FLAG.format(django_target, guid)
    already_done = bool(services.redis.get(redis_key))
    if already_done:
        return []
    django_dicts = cdms_pages(client, guid, odata_target, filters, 0)
    n_django_dicts = len(django_dicts)
    if n_django_dicts:
        LOGGER.info(
            "(%s) -> %s of %s", guid, n_django_dicts, django_target
        )
    retval = leeloo.send(django_target, django_dicts)  # errors recorded here
    services.redis.set(redis_key, datetime.datetime.now().isoformat())
    return retval


def traverse(client, traversal_spec):
    '''
    Download everything, traversing from parent to children. Tee acquired the
    data to the OData database and Leeloo web API.
    '''
    (root_table, root_pkey), children = traversal_spec
    odata_metadata = services.db.get_odata_metadata()
    odata_table = odata_metadata.tables[root_table]
    base_select = sqla.select([odata_table])
    execute = odata_metadata.bind.execute
    odata_chunks = select_chunks(execute, odata_table, base_select)
    for odata_chunk in odata_chunks:
        for odata_row in odata_chunk:
            guid = getattr(odata_row, root_pkey)
            for table_name, parent_alias in children:
                cdms_to_leeloo(
                    client,
                    guid,
                    odata_metadata.tables[table_name],
                    spec.MAPPINGS[table_name]['to'],
                    "{0} eq {1}".format(parent_alias, views.fmt_guid(guid)),
                )


def main():
    traversal_spec = (
        ('AccountSet', 'AccountId'),
        (
            ('ContactSet', 'ParentCustomerId/Id'),
            ('detica_interactionSet', 'optevia_Organisation/Id'),
        ),
    )
    client = CDMSRestApi()
    traverse(client, traversal_spec)
