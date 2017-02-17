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
