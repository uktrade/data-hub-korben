es_index_name = 'datahub'
es_type_name = 'company'
es_mapping = {
    'properties': {
        'id': {'type': 'string', 'index': 'not_analyzed'},
        'title': {'type': 'string', 'index': 'not_analyzed', "boost": 3.0},
        'address_1': {'type': 'string', 'index': 'not_analyzed'},
        'address_2': {'type': 'string', 'index': 'not_analyzed'},
        'address_town': {'type': 'string', 'index': 'no'},
        'address_county': {'type': 'string', 'index': 'no'},
        'address_country': {'type': 'string', 'index': 'no'},
        'address_postcode': {'type': 'string', 'index': 'not_analyzed', "boost": 2.0},
        'alt_address_1': {'type': 'string', 'index': 'not_analyzed'},
        'alt_address_2': {'type': 'string', 'index': 'not_analyzed'},
        'alt_address_town': {'type': 'string', 'index': 'no'},
        'alt_address_county': {'type': 'string', 'index': 'no'},
        'alt_address_country': {'type': 'string', 'index': 'no'},
        'alt_address_postcode': {'type': 'string', 'index': 'not_analyzed', "boost": 2.0},
        'company_number': {'type': 'string', 'index': 'not_analyzed', "boost": 3.0},
        'incorporation_date': {'type': 'date', 'index': 'no'},
        'alt_title': {'type': 'string', 'index': 'not_analyzed', "boost": 3.0},
    }
}
