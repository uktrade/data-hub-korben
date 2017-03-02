# BAU
This package contains a Pyramid web app that offering a web API that allows
basic CRUD operations and an authentication.

## Package structure
 - [`auth`](auth.py) Authenticating incoming requests
 - [`common`](common.py) Code common to `get`, `update`, `create` views
 - [`leeloo`](leeloo.py) Making requests to Leeloo
 - [`poll`](poll.py) Polling OData service for new entries
 - [`status`](status.py) Provide Pingdom status of attached services
 - [`views`](views.py) Endpoints
 - [`webserver`](webserver.py) App config, expose WSGI app

## Endpoints
There are a group of endpoints for retrieving and altering CDMS data, an
endpoint for verfiying CDMS credentials and a an endpoint for providing status
of attached services.

### `create`, `update`, `get`
These views are all very similar, they make an ETL call in each direction on a
single entry; one call from Django -> OData and one back from OData -> Django.

### `validate_credentials`
This view makes a call to `CMDSRestApi.login` with a temporarily created cookie
“file” and responds with true or false in JSON depending on the result of this
call.

### `pingdom`
This view returns the status of the OData database, Redis instance, CDMS and
the polling service in XML for consumption by Pingdom.


## Polling
The [`poll`](poll.py) module offers a CLI for a script that repeatedly makes
calls to the CDMS web API to sync changes made through the CDMS web UI to Data
Hub. Given a list of entity names, a `CDMSPoller` instance will carry out a
“reverse scrape” of each of these entities, teeing fresh data to the
intermediate OData database and Leeloo web API.

### “Reverse scrape” logic
The logic requires a “comparitor” column which is used as a request parameter
([`$orderby`](http://www.odata.org/documentation/odata-version-2-0/uri-conventions/#OrderBySystemQueryOption))
and to determine whether incoming data is newer or older than existing data.
The default value for the comparitor column is `ModifiedOn`, but others are
used in testing (see
[`test/tier0/bau/test_poll`](https://github.com/uktrade/data-hub-korben/blob/master/test/tier0/bau/test_poll.py)).
Using this comparitor;
  - the `PAGE_SIZE` most recent entries are downloaded and individually
    compared to existing rows in the database;
    - if there is no row to compare to, it will be inserted and sent to
      Leeloo;
    - if the row exists and is the same age as the incoming row, it is
      disgarded (the most up-date-version exists already);
    - if the row exists and is older than the incoming row, the incoming
      row is “upserted” into the intermediate database and sent to Leeloo;
  - if all 50 entries result in either an insert or an update, then it is
    assumed that there are further outstanding updates to download for this
    entity type and the offset is incremented and the “next” page is processed
    in the same way.
