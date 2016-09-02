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
    'setup_requires': [
        'pytest-runner',
    ],
    'tests_require': [
        'pytest',
    ],
    'install_requires': [
        'cryptography',
        'django',
        'psycopg2',
        'pyquery',  # >:(
        'pyslet',
        'pyyaml',
        'requests',
        'requests_ntlm',
        'responses',  # >:(
        'sqlalchemy',
        'sqlparse',
    ],
    'entry_points': {
        'console_scripts': [
            'korben=korben.cli:main',
        ],
    },
    'dependency_links': [
        'git+https://github.com/UKTradeInvestment/pyslet.git@master#egg=pyslet',
    ]
}

setuptools.setup(**setup_kwargs)
