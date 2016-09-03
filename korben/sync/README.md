# Sync

Pull data from CDMS, service to poll CDMS for new data, relation traversal for
loading object dependencies. Make appropriate calls to ETL with fresh data.

## [`traverse`](traverse.py)
Get a single object, traversing required dependencies.

## [`poll`](poll.py)
Poll all supported entity types (ie. those with `ModifiedOn` attribute).
