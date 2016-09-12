from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk as es_bulk


def create_index_item(ch_company, action="create"):

    search_item = {
        'id': ch_company.company_number,
        'title': ch_company.company_name,
        'address_1': ch_company.registered_address_address_1,
        'address_2': ch_company.registered_address_address_2,
        'address_town': ch_company.registered_address_town,
        'address_county': ch_company.registered_address_county,
        'address_country': ch_company.registered_address_country,
        'address_postcode': ch_company.registered_address_postcode,
        'company_number': ch_company.company_number,
        'incorporation_date': ch_company.incorporation_date
    }

    metadata = {
        '_op_type': action,
        "_index": search_item.Meta.es_index_name,
        "_type": search_item.Meta.es_type_name,
    }
    data.update(**metadata)
    return data


def dump_buffer(buffer):
    print("Saving")
    es_bulk(
        client=settings.ES_CLIENT,
        actions=buffer,
        stats_only=True,
        chunk_size=1000,
        request_timeout=300)
    print("Saved")


def index_ch():
    buffer = []
    count = 0
    max_buffer = 10000

    paginator = Paginator(CHCompany.objects.all(), max_buffer)

    for page in range(1, paginator.num_pages + 1):
        for ch in paginator.page(page).object_list:
            buffer.append(create_index_item(ch=ch, action='create'))
            print("{0}, {1!s} - {2!s}".format(count, ch.company_number, ch.company_name))
            count += 1

            if count % max_buffer == 0:
                dump_buffer(buffer=buffer)
                buffer = []
                gc.collect()

        gc.collect()

    print("Almost done")
    dump_buffer(buffer=buffer)
    print("Done")


def recreate_index():
    indices_client = IndicesClient(client=client)

    if indices_client.exists(schema.es_index_name):
        indices_client.delete(index=schema.es_index_name)

    indices_client.create(index=schema.es_index_name)

    indices_client.put_mapping(
        doc_type=schema.es_type_name,
        body=schema.es_mapping,
        index=schema.es_index_name
    )
