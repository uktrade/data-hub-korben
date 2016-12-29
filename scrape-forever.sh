#! /bin/bash

until korben sync scrape; do
    echo "Bark!" >&2
    sleep 1
done
