from . import settings


def delete_for_company_number(company_number):
    # Find the existing entry to get it's id
    find_query = {
        "query": {
            "constant_score": {
                "filter": {
                    "term": {
                        "company_number": company_number
                    }
                }
            }
        }
    }

    es_results = settings.ES_CLIENT.search(index=SearchItem.Meta.es_index_name,
                                           doc_type=SearchItem.Meta.es_type_name,
                                           body=find_query)

    if es_results['hits']['total'] == 1:
        index_id = es_results['hits']['hits'][0]['_id']
        delete_for_id(index_id)


def delete_for_source_id(source_id):
    # Find the existing entry to get it's id
    find_query = {
        "query": {
            "constant_score": {
                "filter": {
                    "term": {
                        "source_id": source_id
                    }
                }
            }
        }
    }

    es_results = settings.ES_CLIENT.search(index=SearchItem.Meta.es_index_name,
                                           doc_type=SearchItem.Meta.es_type_name,
                                           body=find_query)

    if es_results['hits']['total'] == 1:
        index_id = es_results['hits']['hits'][0]['_id']
        delete_for_id(index_id)


def delete_for_id(index_id):
    settings.ES_CLIENT.delete(index=SearchItem.Meta.es_index_name,
                              doc_type=SearchItem.Meta.es_type_name,
                              id=index_id,
                              refresh=True)


def search_item_from_ch(ch):
    return SearchItem(
        source_id=ch.company_number,
        result_source="CH",
        result_type="COMPANY",
        title=ch.company_name,
        address_1=ch.registered_address_address_1,
        address_2=ch.registered_address_address_2,
        address_town=ch.registered_address_town,
        address_county=ch.registered_address_county,
        address_country=ch.registered_address_country,
        address_postcode=ch.registered_address_postcode,
        company_number=ch.company_number,
        incorporation_date=ch.incorporation_date
    )



# Generate an elastic search item from a contact record
def search_item_from_contact(contact):
    return SearchItem(
        source_id=contact.id,
        result_source='DIT',
        result_type='CONTACT',
        title=contact.first_name + ' ' + contact.last_name,
        address_1=contact.address_1,
        address_2=contact.address_2,
        address_town=contact.address_town,
        address_county=contact.address_county,
        address_country=contact.address_country,
        address_postcode=contact.address_postcode
    )


# Generate an elastic search item from an interaction record
def search_item_from_interaction(interaction):
    return SearchItem(
        source_id=interaction.id,
        result_source='DIT',
        result_type='INTERACTION',
        title=interaction.title
    )
