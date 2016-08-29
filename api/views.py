import json
from django.http import HttpResponse
from django.conf import settings
from rest_framework import viewsets
from api.models import CHCompany, SearchItem, Company
from .serializers import CHCompanySerializer, CompanySerializer


class CHCompanyViewSet(viewsets.ModelViewSet):
    queryset = CHCompany.objects.all()
    serializer_class = CHCompanySerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

def search(request):
    term = request.GET.get('term','')
    data = {
        "query": {
            "query_string": {"query": term}
        }
    }

    # Todo - Add facets
    index_name=SearchItem.Meta.es_index_name
    res = settings.ES_CLIENT.search(index=index_name, body=data)
    res['hits']['query'] = term;
    return HttpResponse(json.dumps(res['hits']), content_type='application/json')
