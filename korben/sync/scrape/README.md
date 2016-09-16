# Scrape
Make an effort to download everything available in CDMS using the OData
endpoint. The approach is simple; page through all entities named in
[`/$metadata`](http://www.odata.org/documentation/odata-version-2-0/overview/#ServiceMetadataDocument)
downloading
[atom](http://www.odata.org/documentation/odata-version-2-0/atom-format/)
responses and parsing `<entry>` elements into CSV files containing rows
destined for the schema defined using `/$metadata` by
[`odata_psql`](../../odata_psql).

## Usage
With a properly configured Korben instance, the scrape process can be started
with `korben sync scrape`. It takes a long time to download all entity types,
so be patient. There is a degree of logging output to allow the user to monitor
progress.
