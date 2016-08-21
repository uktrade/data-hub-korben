from django.test import TestCase
from .serializers import CHCompanySerializer, SearchIndexSerializer
from api.models import CHCompany, SearchIndex


class SearchIndexSerializerTests(TestCase):

    def test_serialiser(self):
        search_index = SearchIndex(
            source_id="123",
            source_type="COMPANY",
            title="My great company",
            summary="something that is shown in the search results",
            postcode="SL4 4QR")

        serializer = SearchIndexSerializer(search_index)
        print(serializer.data)
