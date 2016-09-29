#!/usr/bin/env python
import setuptools


DESCRIPTION = 'Codebase for sync/ETL/search service, Django "client" for CDMS'
SETUP_KWARGS = {
    'name': 'korben',
    'version': '1.0',
    'description': DESCRIPTION,
    'author': 'B M Corser',
    'author_email': 'ben@steady.supply',
    'packages': setuptools.find_packages(),
    'entry_points': {
        'console_scripts': [
            'korben=korben.cli:main',
        ],
    },
}

setuptools.setup(**SETUP_KWARGS)
