import json
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from api.models.chcompany import CHCompany
from api.models.company import Company
from api.models.searchitem import search_item_from_company
from api.serializers import CHCompanySerializer, CompanySerializer
from rest_framework.response import Response
from api.services.searchservice import search as search_es


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class CHCompanyViewSet(viewsets.ModelViewSet):
    queryset = CHCompany.objects.all()
    serializer_class = CHCompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_company = serializer.save()
        search_item = search_item_from_company(new_company)
        search_item.add()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def search(request):
    term = request.GET.get('term', '')
    result = search_es(term=term)
    return HttpResponse(json.dumps(result), content_type='application/json')
