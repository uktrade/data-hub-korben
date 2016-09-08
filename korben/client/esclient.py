def save(self):
    try:
        serializer = SearchItemSerializer(self)
        data = serializer.data
        settings.ES_CLIENT.create(index=self.Meta.es_index_name,
                                  doc_type=self.Meta.es_type_name,
                                  body=data,
                                  refresh=True)
    except Exception as inst:
        print(inst)

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
