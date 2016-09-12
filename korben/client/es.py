from . import schema
from .client import client

def company_searchitem(company):
    '''
    ch = CHCompany.objects.get(pk=company.company_number)   # Go and get the companies house entry from the DB
    if company.company_number and len(company.company_number) > 0:
        result_source = 'COMBINED'
    else:
        result_source = 'DIT'
    '''
    ch = object()
    return {
        'source_id': company.id,
        'result_source': result_source,
        'result_type': 'COMPANY',
        'title': None,  # ch.company_name,
        'address_1': None,  # ch.registered_address_address_1,
        'address_2': None,  # ch.registered_address_address_2,
        'address_town': None,  # ch.registered_address_town,
        'address_county': None,  # ch.registered_address_county,
        'address_country': None,  # ch.registered_address_country,
        'address_postcode': None,  # ch.registered_address_postcode,
        'alt_title': company.trading_name,
        'alt_address_1': company.trading_address_1,
        'alt_address_2': company.trading_address_2,
        'alt_address_town': company.trading_address_town,
        'alt_address_county': company.trading_address_county,
        'alt_address_country': company.trading_address_country,
        'alt_address_postcode': company.trading_address_postcode,
        'company_number': company.company_number,
        'incorporation_date': None,  # ch.incorporation_date
    }

def save(company):
    es_client.create(
        index=schema.es_index_name,
        doc_type=schema.es_type_name,
        body=company_searchitem(company),
        refresh=True,
    )

def check_ch_data(request):
    # look at the incoming data. Is there a company number?
    # if so then lookup some CH data and add it here before turning it
    # into a company.
    if request.data['company_number'] and len(request.data['company_number']) > 0:
        ch = CHCompany.objects.get(pk=request.data['company_number'])
        request.data['registered_name'] = ch.company_name
        request.data['business_type'] = ch.company_category

def create(self, request, **kwargs):

    # Delete the existing index entry and create a new one.
    if request.data['company_number'] and len(request.data['company_number']) > 0:
        delete_for_company_number(new_company.company_number)

    search_item = search_item_from_company(new_company)
    search_item.save()


def update(self, request, *args, **kwargs):

    delete_for_source_id(company.id)
    search_item = search_item_from_company(company)
    search_item.save()
