# Sync

Pull data from CDMS, service to poll CDMS for new data, relation traversal for
loading object dependencies. Make appropriate calls to ETL with fresh data.

## [`traverse`](traverse.py)
Get a single object, traversing required dependencies.

## [`poll`](poll.py)
Poll for new rows in remoted tables mentioned in `etl.spec.MAPPINGS`, make
updates based on `ModifiedOn` attribute.

## [`populate`](populate.py)
Load pickled responses, convert their XML content into CSV files and use `COPY`
to throw them into the database.
