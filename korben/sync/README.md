# Initial setup

``` python
from korben.cdms_api.rest.api import CDMSRestApi

client = CDMSRestApi()
client.create(
    'optevia_businesstypeSet',
    {
        'optevia_businesstypeId': '9ed14e94-5d95-e211-a939-e4115bead28a',
        'optevia_name': 'Private limited company'
    }
)
client.create(
    'optevia_businesstypeSet',
    {
        'optevia_businesstypeId': '9fd14e94-5d95-e211-a939-e4115bead28a',
        'optevia_name': 'Public limited company'
    }
)
```
