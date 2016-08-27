# Korben
![Korben](korben-dallas.jpg)

_Korben talks to CDMS_

This repo contains application code for a service providing CDMS sync, an ETL
“pipeline” for getting data to a standard Django-controlled database, and
search indexing. It offers a web API for search, to trigger sync. It also
provides a Django client library for “reverse ETL” allowing Django objects to
be written back to CDMS.

# Contents

 - [Sync](#sync)
 - [ETL](#etl)
 - [Search](#search)
 - [Client](#client)

# Sync
Pull data from CDMS, service to poll CDMS for new data, relation traversal for
loading object dependencies. Make appropriate calls to ETL with fresh data.

# ETL
Map data from CDMS schema to Django schema, populate/update Django database.

# Search
Load data into ElasticSearch.

# Client
Provide CRUD functions which talk about Django model objects, but handle
individual CDMS sync operations “behind the scenes”. Provide search API.
