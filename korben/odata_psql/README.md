# Tools for converting OData `metadata.xml` to PostgreSQL schema

CDMS exposes an OData endpoint, which provides access to data in what is hoped to be the
schema for the MSSQL(?) databases underlying MS Dynamics instance. This
directory contains scripts that take in the XML file exposed at `/$metadata`
describing the data’s schema and output SQL files describing the same schema
for Postgres.

In the case of CDMS, the SQL schema output by these scripts has very long
column names. There is a Docker container [here](../../../postgres-namedatalen)
that can handle these.

## Usage
The command line interface to these scripts takes two arguments; the name of
the input metadata file and the name of the output SQL file. For example:

```
korben odata-psql metadata.xml schema.sql
```
