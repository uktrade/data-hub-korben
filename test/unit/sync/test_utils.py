import pytest
import json
import os

from korben.sync import utils


CASES = (
    ('odata-supplier.json', {
        'Address_City': 'Redmond',
        'Address_Country': 'USA',
        'Address_State': 'WA',
        'Address_Street': 'NE 40th',
        'Address_ZipCode': '98052',
        'Concurrency': 0,
        'ID': 1,
        'Name': 'Tokyo Traders',
    }),
    ('odata-product.json', {
        'Description': '1080P Upconversion DVD Player',
        'DiscontinuedDate': None,
        'ID': 7,
        'Name': 'DVD Player',
        'Price': '35.88',
        'Rating': 3,
        'ReleaseDate': '2006-11-15 00:00:00',
    }),
    ('odata-category.json', {'ID': 2, 'Name': 'Electronics'}),
)


@pytest.mark.parametrize('name,expected', CASES)
def test_entry_row(odata_utils, name, expected):
    fixtures_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..', 'tier0', 'fixtures'
    )
    with open(os.path.join(fixtures_path, name), 'r') as entry_fh:
        entry = json.loads(entry_fh.read())
    result = odata_utils.entry_row(None, entry['d'])
    assert result == expected
