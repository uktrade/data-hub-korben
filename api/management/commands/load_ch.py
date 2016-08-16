import csv
from django.core.management.base import BaseCommand, CommandError
from api.models import CHCompany

DATE_FIELDS = (
    'accounts_next_due_date',
    'incorporation_date',
    'dissolution_date',
    'accounts_last_made_up_date',
    'returns_next_due_date',
    'returns_last_made_up_date',
)

INT_FIELDS = (
    'accounts_accounting_ref_day',
    'accounts_accounting_ref_month',
    'mortgages_num_mort_charges',
    'mortgages_num_mort_outstanding',
    'mortgages_num_mort_part_satisfied',
    'mortgages_num_mort_satisfied',
    'limited_partnerships_num_gen_partners',
    'limited_partnerships_num_lim_partners',
)


class Command(BaseCommand):
    help = 'Load Companies House CSV'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    @staticmethod
    def parse_dates(row):
        for key in row:
            if row[key] is not None and key in DATE_FIELDS or row[key] is not None and 'date' in key:
                day, month, year = row[key].split('/')
                row[key] = "{0}-{1}-{2}".format(year, month, day)

    @staticmethod
    def parse_ints(row):
        for key in row:
            if row[key] is not None and key in INT_FIELDS:
                row[key] = int(row[key])

    @staticmethod
    def clear_empty(row):
        for key in row:
            if len(row[key]) == 0:
                row[key] = None

    def handle(self, filename, *args, **options):
        # Open the csv file and parse as a collection of dictionaries
        with open(filename, 'r') as csv_fh:
            rows = list(csv.DictReader(csv_fh))

        count = 0

        # Iterate through reach row, converting dates and numbers before saving
        for row in rows:
            if CHCompany.objects.filter(company_number=row['company_number']).exists():
                print("{0!s} already exists".format(row['company_number']))
            else:
                count += 1
                self.clear_empty(row)
                self.parse_dates(row)
                self.parse_ints(row)

                print("{0}, {1!s} - {2!s}".format(count, row['company_number'], row['company_name']))
                CHCompany.objects.get_or_create(**row)
