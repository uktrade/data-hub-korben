import datetime

from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk

from .client import client
from . import schema


def chcompany_searchitem(row, add_metadata=True):

    if row['incorporation_date'] is not None:
        day, month, year = row['incorporation_date'].split('/')
        incorporation_date = datetime.date(int(year), int(month), int(day))
    else:
        incorporation_date = None

    searchitem = {
        'source_id': row['company_number'],
        'result_source': "CH",
        'result_type': "COMPANY",
        'title': row['company_name'],
        'address_1': row['registered_address_address_1'],
        'address_2': row['registered_address_address_2'],
        'address_town': row['registered_address_town'],
        'address_county': row['registered_address_county'],
        'address_country': row['registered_address_country'],
        'address_postcode': row['registered_address_postcode'],
        'company_number': row['company_number'],
        'incorporation_date': incorporation_date
    }

    if add_metadata is True:
        searchitem.update({
            '_op_type': 'create',
            "_index": schema.es_index_name,
            "_type": schema.es_type_name,
        })

    return searchitem


def create_index():
    indices_client = IndicesClient(client=client)
    if not indices_client.exists(schema.es_index_name):
        indices_client.create(index=schema.es_index_name)
        indices_client.put_mapping(
            doc_type=schema.es_type_name,
            body=schema.es_mapping,
            index=schema.es_index_name
        )


def dump_buffers(ch_buffer, index_buffer):
    bulk(
        client=client,
        actions=index_buffer,
        stats_only=True,
        chunk_size=1000,
        request_timeout=300,
    )


def main():
    pass
