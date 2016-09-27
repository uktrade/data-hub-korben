import os

from lxml import etree
from korben.sync import utils

def test_entry_row():
    fixtures_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'fixtures'
    )
    with open(os.path.join(fixtures_path, 'product-entry.xml'), 'rb') as entry_fh:
        entry = etree.fromstring(entry_fh.read())
    result = utils.entry_row(None, None, entry)
    expected = {
        'ID': '7',
        'ReleaseDate': '2006-11-15 00:00:00',
        'Rating': '3',
        'DiscontinuedDate': None,
        'Price': '35.88',
    }
    assert result == expected
