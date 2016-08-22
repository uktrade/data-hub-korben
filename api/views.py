from rest_framework import viewsets
from .serializers import CHCompanySerializer
from api.models import CHCompany
from django.http import HttpResponse
import json
import requests
from django.conf import settings

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

    url = "{0}datahub/_search".format(settings.ES_HOST)

    response = requests.post(url, data=json.dumps(data))
    return HttpResponse(response, content_type='application/json')

