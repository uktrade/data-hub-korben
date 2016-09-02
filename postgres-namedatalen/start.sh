#!/bin/bash

if [ -n /var/lib/postgresql/data/sss ];
    /usr/local/pgsql/bin/initdb /usr/local/var/postgres
done

/usr/local/pgsql/bin/pg_ctl -D /usr/local/var/postgres -l logfile start
