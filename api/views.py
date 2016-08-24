import json
from django.http import HttpResponse
from django.conf import settings
from rest_framework import viewsets
from api.models import CHCompany, SearchItem
from .serializers import CHCompanySerializer


class CHCompanyViewSet(viewsets.ModelViewSet):
    queryset = CHCompany.objects.all()
    serializer_class = CHCompanySerializer


def search(request):
    term = request.GET.get('term','')
    data = {
        "query": {
            "query_string": {"query": term}
        }
    }

    index_name=SearchItem.Meta.es_index_name
    res = settings.ES_CLIENT.search(index=index_name, body=data)
    return HttpResponse(json.dumps(res['hits']), content_type='application/json')
