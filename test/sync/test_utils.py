import os

from lxml import etree
from korben.sync import utils

CASES = (
    ('product-entry.xml', {
        'ID': '7',
        'ReleaseDate': '2006-11-15 00:00:00',
        'Rating': '3',
        'DiscontinuedDate': None,
        'Price': '35.88',
    }),
    ('supplier-entry.xml', {
        'Name': 'Exotic Liquids',
        'ID': '0',
        'Concurrency': '0',
        'Address_State': 'WA',
        'Address_Street': 'NE 228th',
        'Address_Country': 'USA',
        'Address_ZipCode': '98074',
        'Address_City': 'Sammamish',
    }),
)

def test_entry_row(odata_sync_utils):
    fixtures_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'fixtures'
    )
    for name, expected in CASES:
        with open(os.path.join(fixtures_path, name), 'rb') as entry_fh:
            entry = etree.fromstring(entry_fh.read())
        result = utils.entry_row(None, None, entry)
        assert result == expected
