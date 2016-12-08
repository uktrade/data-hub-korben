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
