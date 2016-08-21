import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk
from api.models import CHCompany
from api.serializers import CHCompanySerializer

DATE_FIELDS = (
    'incorporation_date',
)

FIELDS = (
    'company_number',
    'company_name',
    'registered_address_care_of',
    'registered_address_po_box',
    'registered_address_address_1',
    'registered_address_address_2',
    'registered_address_town',
    'registered_address_county',
    'registered_address_country',
    'registered_address_postcode',
    'company_category',
    'company_status',
    'sic_code_1',
    'sic_code_2',
    'sic_code_3',
    'sic_code_4',
    'uri'
)


class Command(BaseCommand):
    help = 'Load Companies House CSV'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, filename, *args, **options):

        print("Creating Index in elasticsearch")
        self.create_index()

        # Open the csv file and parse as a collection of dictionaries
        with open(filename, 'r') as csv_fh:
            rows = list(csv.DictReader(csv_fh))

        count = 0
        max_buffer = 10000
        pos = 0
        buffer = []

        # Iterate through reach row and build a new company record in a buffer
        for row in rows:
            if CHCompany.objects.filter(company_number=row['company_number']).exists():
                print("{0!s} already exists".format(row['company_number']))
            else:
                buffer.append(self.create_company(row))
                pos += 1
                count += 1

                print("{0},{1} {2!s} - {3!s}".format(count, pos, row['company_number'], row['company_name']))

                if pos == max_buffer:
                    self.dump(buffer)
                    pos = 0
                    buffer = []

        print("Finished, saving remaining records.")
        self.dump(buffer)

    def dump(self, buffer):
        print("Dumping to DB")
        CHCompany.objects.bulk_create(buffer)
        print("Saving to index")
        self.push_buffer_to_index(buffer)
        print("Indexed")

    def create_company(self, row):
        data = {}

        for key in FIELDS:
            if len(row[key]) == 0:
                row[key] = None

            if row[key] is not None and key in DATE_FIELDS or row[key] is not None and 'date' in key:
                day, month, year = row[key].split('/')
                data[key] = "{0}-{1}-{2}".format(year, month, day)
            else:
                data[key] = row[key]

        company = CHCompany(**data)

        return company

    def create_index(self):
        indices_client = IndicesClient(client=settings.ES_CLIENT)
        index_name = CHCompany._meta.es_index_name

        if not indices_client.exists(index_name):
            indices_client.create(index=index_name)

            indices_client.put_mapping(
                doc_type=CHCompany._meta.es_type_name,
                body=CHCompany._meta.es_mapping,
                index=index_name
            )

    def push_buffer_to_index(self, buffer):
        data = [self.convert_for_index(company, 'create') for company in buffer]
        bulk(client=settings.ES_CLIENT, actions=data, stats_only=True)

    def convert_for_index(self, company, action=None):
        serializer = CHCompanySerializer(company)
        data = serializer.data
        metadata = {
            '_op_type': action,
            "_index": company._meta.es_index_name,
            "_type": company._meta.es_type_name,
        }
        data.update(**metadata)
        return data
