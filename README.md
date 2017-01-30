# Korben
![Korben](docs/assets/korben-dallas.jpg)

_Korben talks to CDMS_

![Data flow](docs/assets/korben-data-flow.png)

_Data flow in Korben_

This directory contains application code for a service offering two-way CDMS
sync. It also contains code for loading CDMS and CH data into an Elastic Search
index.

# Initial

Run the following commands from the Korben container to get the system
populated with initial dataset:
``` bash
# Download everything we can from Dynamics instance
# and dump into OData database
korben sync scrape

# Download Companies House data, transform and insert
# into Django database
korben sync ch

# Transform relevant contents of OData database
# and insert into Django database
korben sync django

# Dump entire contents of Django database into ElasticSearch index
korben sync es
```

# BAU
There are two web applications offered by this package. One is a web API
allowing an authenticated request to trigger CRUD operations on a Dynamics
instance. It’s a WSGI application and can be easily invoked by running
`korben bau` on the command line. The other is a simple Python script which
polls a Dynamics instance for fresh data. It can be invoked with `korben bau
poll`. This service doesn’t offer an interface.

# Testing
There are three test suites in this repository, two of which have test
environments defined here. The first contains basic unit tests; `make
test-unit`, the second has an environment suitable for writing tests against a
reference OData implementation offered by Microsoft (see
http://www.odata.org/odata-services/); `make test-tier0`, and the third is a
suite designed to run against the staging CDMS instance, with whatever
implementation of OData that is offered by Microsoft CRM 2011. There isn’t a
Make command for it here, because it has a dependency on
[`uktrade/data-hub-leeloo`](https://github.com/uktrade/data-hub-leeloo),
instead refer to the “umbrella” repo
[`uktrade/data-hub`](https://github.com/uktrade/data-hub).
