import os

PROCESSES = int(os.environ.get('KORBEN_SCRAPE_PROCESSES', 16))
CHUNKSIZE = 100
PAGESIZE = 50
INTERVAL = int(os.environ.get('KORBEN_SCRAPE_INTERVAL', 5))

SECRET_SECTORS = (
    '9e38cecc-5f95-e211-a939-e4115bead28a',
    'ae22c9d2-5f95-e211-a939-e4115bead28a',
    'a738cecc-5f95-e211-a939-e4115bead28a',
    'b222c9d2-5f95-e211-a939-e4115bead28a',
    'ab38cecc-5f95-e211-a939-e4115bead28a',
    'a422c9d2-5f95-e211-a939-e4115bead28a',
    'a238cecc-5f95-e211-a939-e4115bead28a',
    'a938cecc-5f95-e211-a939-e4115bead28a',
    '7ebb9fc6-5f95-e211-a939-e4115bead28a',
    '9738cecc-5f95-e211-a939-e4115bead28a',
    'a822c9d2-5f95-e211-a939-e4115bead28a',
    '7dbb9fc6-5f95-e211-a939-e4115bead28a',
    'af22c9d2-5f95-e211-a939-e4115bead28a',
    'a038cecc-5f95-e211-a939-e4115bead28a',
    'a438cecc-5f95-e211-a939-e4115bead28a',
    '9838cecc-5f95-e211-a939-e4115bead28a',
    'a622c9d2-5f95-e211-a939-e4115bead28a',
    'aa38cecc-5f95-e211-a939-e4115bead28a',
    'ac22c9d2-5f95-e211-a939-e4115bead28a',
    'a538cecc-5f95-e211-a939-e4115bead28a',
    '9538cecc-5f95-e211-a939-e4115bead28a',
    'a338cecc-5f95-e211-a939-e4115bead28a',
    '9938cecc-5f95-e211-a939-e4115bead28a',
    '9638cecc-5f95-e211-a939-e4115bead28a',
    '9f38cecc-5f95-e211-a939-e4115bead28a',
    'a922c9d2-5f95-e211-a939-e4115bead28a',
    '9b38cecc-5f95-e211-a939-e4115bead28a',
    '9a38cecc-5f95-e211-a939-e4115bead28a',
    'b822c9d2-5f95-e211-a939-e4115bead28a',
    'a138cecc-5f95-e211-a939-e4115bead28a',
    'a722c9d2-5f95-e211-a939-e4115bead28a',
    '9d38cecc-5f95-e211-a939-e4115bead28a',
    'aa22c9d2-5f95-e211-a939-e4115bead28a',
    'a838cecc-5f95-e211-a939-e4115bead28a',
    'a638cecc-5f95-e211-a939-e4115bead28a',
    'ad22c9d2-5f95-e211-a939-e4115bead28a',
)
