# Initial setup

Long-running scrape to populate `datahub_odata` database is executed with
`korben sync scrape`. Sit back and relax, this takes hours.

When the “staging” `datahub_odata` database is populated, let’s run the initial
ETL to get that data into the Django database `datahub`. Just run
`korben sync django`.

Now download and populate the Django database with Companies House Data. This
also takes some time (45 mins). Run `korben sync ch`.

Next let’s populate the ElasticSearch instance `korben sync es`.

Leeloo is now populated and ready to rock.

We also need to update CDMS with the enum rows we use to represent `Undefined`,
we need to copy the latest fixtures out of the `leeloo` directory (damn it,
Docker) and then use another sync command to send those fixtures to CDMS:
```
cp leeloo/fixtures/undefined.yaml leeloo/fixtures/datahub_businesstypes.yaml korben/leeloo_fixtures
korben sync cdms korben/leeloo_fixtures/undefined.yaml korben/leeloo_fixtures/datahub_businesstypes.yaml
```
