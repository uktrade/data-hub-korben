import functools
import logging

import elasticsearch
from elasticsearch import helpers as es_helpers
import sqlalchemy as sqla
from sqlalchemy.sql import functions as sqla_func

from korben import services
from korben import etl
from korben.services import es
from . import constants
from . import utils


LOGGER = logging.getLogger('korben.sync.es_initital')


def row_es_add(table, es_id_col, row):
    'Create an ES `index` action from a database row'
    return {
        '_op_type': 'index',
        "_index": etl.spec.ES_INDEX,
        "_type": table.name,
        "_id": row[es_id_col],
        "_source": dict(row),
    }


def setup_index():
    '''
    Assume that if the index exists it is complete, otherwise create it and
    populate with mappings
    '''
    indices_client = elasticsearch.client.IndicesClient(
        client=services.es.client
    )
    if not indices_client.exists(etl.spec.ES_INDEX):
        indices_client.create(index=etl.spec.ES_INDEX)
        for doc_type, body in etl.spec.get_es_types().items():
            indices_client.put_mapping(
                doc_type=doc_type,
                body=body,
                index=etl.spec.ES_INDEX,
            )


def get_remote_name_select(cols):
    'Get either the `name` column or `first_name` ++ `last_name`'
    if hasattr(cols, 'name'):
        return cols.name
    if all(map(functools.partial(hasattr, cols), ('first_name', 'last_name'))):
        return (
            sqla_func.coalesce(getattr(cols, 'first_name'), '')
            +
            sqla_func.coalesce(getattr(cols, 'last_name'), '')
        )

def joined_select(table):
    fkey_data_cols = []
    joined = table
    # knock together the joins in a general, if rather assumptive manner
    joined_tables = set()
    for col in filter(lambda col: bool(col.foreign_keys), table.columns):
        fkey = next(iter(col.foreign_keys))  # assume fkeys
                                             # are non-composite
        # don’t try to join twice
        if fkey.column.table.name not in joined_tables:
            # outer join is used here because data from cdms is incomplete
            # TODO: make scrape code more thorough, or maybe fix etl
            joined = joined.outerjoin(
                fkey.column.table,
                onclause=fkey.column.table.c.id == col  # assume join clause is
            )                                           # this simple
            joined_tables.add(fkey.column.table.name)
        # label column to lose `_id` suffix
        local_name = col.name[:-3]
        remote_name_select = get_remote_name_select(fkey.column.table.c)
        fmt_str =\
            'Table {0} doesn’t have a recognised name column for fkey {1}.{2}'
        if remote_name_select is None:
            raise RuntimeError(
                fmt_str.format(fkey.column.table.name, table.name, col.name)
            )
        else:
            fkey_data_cols.append(remote_name_select.label(local_name))
    cols = list(filter(lambda col: not bool(col.foreign_keys), table.columns))
    return sqla.select(cols + fkey_data_cols, from_obj=joined)


def main():
    django_metadata = services.db.get_django_metadata()
    setup_index()
    for name in constants.INDEXED_ES_TYPES:
        LOGGER.info("Indexing from django database for {0}".format(name))
        table = django_metadata.tables[name]
        chunks = utils.select_chunks(
            django_metadata.bind.execute, table, joined_select(table)
        )
        for rows in chunks:
            actions = list(map(functools.partial(row_es_add, table, 'id'), rows))
            success_count, error_count = elasticsearch.helpers.bulk(
                client=services.es.client,
                actions=actions,
                stats_only=True,
                chunk_size=1000,
                request_timeout=300,
            )
            assert error_count is 0

    # do ch company logic
    name = 'company_companieshousecompany'
    company_table = django_metadata.tables['company_company']
    result = django_metadata.bind.execute(
        sqla.select([company_table.columns['company_number']])
            .where(company_table.columns['company_number'] != None)  # NOQA
    ).fetchall()
    linked_companies = frozenset([x.company_number for x in result])
    table = django_metadata.tables[name]
    chunks = utils.select_chunks(
        django_metadata.bind.execute, table, joined_select(table)
    )
    for rows in chunks:
        filtered_rows = filter(
            lambda row: row.company_number not in linked_companies, rows
        )
        actions = list(map(
            functools.partial(row_es_add, table, 'company_number'),
            filtered_rows
        ))
        success_count, error_count = elasticsearch.helpers.bulk(
            client=services.es.client,
            actions=actions,
            stats_only=True,
            chunk_size=10,
            request_timeout=300,
            raise_on_error=True,
            raise_on_exception=True,
        )
        assert error_count is 0
