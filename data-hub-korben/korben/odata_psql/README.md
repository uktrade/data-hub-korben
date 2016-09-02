# Tools for converting OData `metadata.xml` to PostgreSQL schema

CDMS exposes an OData endpoint, which in turn exposes what is hoped to be the
schema for the underlying MS Dynamics instance. This directory contains scripts
that take in the `metadata.xml` file describing the OData endpoint’s schema and
output an SQL file describing the same schema for Postgres.

There is also a Bash script and Git patch for producing a properly configured
Postgres installation (allowing for long column names). It is tested on OSX El
Capitan, but should run on Linux too.

## Usage

The scripts are “packaged” by the entrypoint `main.py` which can be run from
the command line and takes two arguments; the name of the input metadata file
and the name of the output SQL file. For example:

```
korben odata-psql metadata.xml schema.sql
```
