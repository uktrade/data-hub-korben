import functools

import elasticsearch

from korben import services
from korben import config
from korben import etl


def row_es_add(doc_type, row):
    'Create an ES add action from a database row'
    es_document = dict(row)
    es_document.update({
        '_op_type': 'add',
        "_index": etl.spec.ES_INDEX,
        "_type": doc_type,
    })
    return es_document


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
        if name == 'company_companyhousecompany':
            continue
        table = django_metadata.tables[name]
        rows = django_metadata.bind.execute(table.select()).fetchall()
        actions = map(functools.partial(row_es_add, name), rows)
        elasticsearch.helpers.bulk(
            client=services.es.client,
            actions=actions,
            stats_only=True,
            chunk_size=1000,
            request_timeout=300,
        )
    company_table = django_metadata.tables['company_company']
    result = django_metadata.bind.execute(
        sqla.select([company_table.columns['company_number']])
    ).fetchall()
    linked_companies = set([x.company_number for x in result])
    if name == 'company_companyhousecompany':
        pass
