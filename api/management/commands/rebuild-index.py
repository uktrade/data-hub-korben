from elasticsearch.client import IndicesClient
from django.conf import settings
from django.core.management.base import BaseCommand
from api.models import CHCompany
from elasticsearch.helpers import bulk
from api.serializers import CHCompanySerializer


class Command(BaseCommand):

    help = 'Recreate Index'

    def handle(self, *args, **options):
        self.recreate_index()
        self.push_db_to_index()

    def recreate_index(self):
        indices_client = IndicesClient(client=settings.ES_CLIENT)
        index_name = CHCompany._meta.es_index_name

        if indices_client.exists(index_name):
            indices_client.delete(index=index_name)

        indices_client.create(index=index_name)

        indices_client.put_mapping(
            doc_type=CHCompany._meta.es_type_name,
            body=CHCompany._meta.es_mapping,
            index=index_name
        )

    def push_db_to_index(self):
        data = [
            self.convert_for_bulk(company, 'create') for company in CHCompany.objects.all()
        ]
        bulk(client=settings.ES_CLIENT, actions=data, stats_only=True)

    def convert_for_bulk(self, django_object, action=None):
        serializer = CHCompanySerializer(django_object)
        data = serializer.data
        metadata = {
            '_op_type': action,
            "_index": django_object._meta.es_index_name,
            "_type": django_object._meta.es_type_name,
        }
        data.update(**metadata)
        return data
