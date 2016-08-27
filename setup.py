#!/usr/bin/env python

import setuptools

DESCRIPTION = 'Codebase for sync/ETL/search service, Django "client" for CDMS'
setup_kwargs = {
    'name': 'data-hub-korben',
    'version': '1.0',
    'description': DESCRIPTION,
    'author': 'B M Corser',
    'author_email': 'ben@steady.supply',
    'packages': ['korben'],
}

setuptools.setup(**setup_kwargs)
