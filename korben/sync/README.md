# Initial setup

Long-running scrape to populate `datahub_odata` database is executed with
`korben sync scrape`. Sit back and relax, this takes hours. Refer to the
[`scrape`](scrape) package for more detailed documentation.

When the “staging” `datahub_odata` database is populated, let’s run the initial
ETL to get that data into the Django database `datahub`. Just run
`korben sync django`.

Now download and populate the Django database with Companies House Data. This
also takes some time (45 mins). Run `korben sync ch`.

Next let’s populate the ElasticSearch instance `korben sync es`.

Leeloo is now populated and ready to rock.

## [`django_initial`](django_initial.py)
This script makes an ETL run to send all entity types specified in the
`etl.spec.MAPPINGS` constant to Django.

> This code breaks the stated “architecture” of Leeloo being separated from
> Korben by inserting rows directly into the Django-controlled database.

As rows are sent to the Django database, any integrity errors found are parsed
for a list entities which were found to be missing. An attempt is then made to
download these missing entities from CDMS. If this fails after
