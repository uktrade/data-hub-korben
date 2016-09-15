import functools

import elasticsearch
from elasticsearch import helpers as es_helpers
import sqlalchemy as sqla

from korben import services
from korben import config
from korben import etl


def row_es_add(doc_type, id_key, row):
    'Create an ES add action from a database row'
    return {
            '_op_type': 'index',
            "_index": etl.spec.ES_INDEX,
            "_type": doc_type,
            "_id": row[id_key],
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
        for doc_type, body in etl.spec.ES_TYPES.items():
            indices_client.put_mapping(
                doc_type=doc_type,
                body=body,
                index=etl.spec.ES_INDEX,
            )


def main():
    django_metadata = services.db.poll_for_metadata(config.database_url)
    setup_index()
    for name in etl.spec.DJANGO_LOOKUP:
        if name == 'company_companieshousecompany':
            continue
        table = django_metadata.tables[name]
        rows = django_metadata.bind.execute(table.select()).fetchall()
        actions = map(functools.partial(row_es_add, name, 'id'), rows)
        es_helpers.bulk(
            client=services.es.client,
            actions=actions,
            stats_only=True,
            chunk_size=1000,
            request_timeout=300,
        )

    # do ch company logic
    name = 'company_companieshousecompany'
    company_table = django_metadata.tables['company_company']
    result = django_metadata.bind.execute(
        sqla.select([company_table.columns['company_number']])
            .where(company_table.columns['company_number'] != None)
    ).fetchall()
    linked_companies = frozenset([x.company_number for x in result])
    table = django_metadata.tables[name]
    rows = django_metadata.bind.execute(table.select()).fetchall()
    filtered_rows = filter(
        lambda row: row.company_number in linked_companies, rows
    )
    actions = map(
        functools.partial(row_es_add, name, 'company_number'), filtered_rows
    )
    elasticsearch.helpers.bulk(
        client=services.es.client,
        actions=actions,
        stats_only=True,
        chunk_size=10,
        request_timeout=300,
        raise_on_error=True,
        raise_on_exception=True,
    )
