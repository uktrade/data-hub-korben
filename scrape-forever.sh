#! /bin/bash

export LD_LIBRARY_PATH=/usr/local/pgsql/lib
export KORBEN_CONF_PATH=staging.yml

until korben sync scrape; do
    echo "Bark!" >&2
    sleep 1
done
