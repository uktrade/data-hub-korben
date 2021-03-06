# Scrape
Make an effort to download everything available in CDMS using the OData
endpoint. The approach is simple; page through all entities named in
[`/$metadata`](http://www.odata.org/documentation/odata-version-2-0/overview/#ServiceMetadataDocument)
downloading
[JSON](http://www.odata.org/documentation/odata-version-2-0/json-format/)
documents and parsing objects into CSV files containing rows destined for the
schema defined (using `/$metadata`) by
[`data-hub-odata-psql`](https://github.com/uktrade/data-hub-odata-psql).

## Usage
With a properly configured Korben instance, the scrape process can be started
with `korben sync scrape`. It takes a long time to download all entity types,
so be patient. There is a degree of logging output to allow the user to monitor
progress. Scrape progress is recorded in Redis, so process can be started and
stopped as required.
