#! /bin/bash

export LD_LIBRARY_PATH=/usr/local/pgsql/lib
export KORBEN_CONF_PATH=staging.yml

until korben sync scrape optevia_businesstypeSet,optevia_sectorSet,optevia_employeerangeSet,optevia_turnoverrangeSet,optevia_ukregionSet,optevia_countrySet,optevia_titleSet,optevia_contactroleSet,optevia_interactioncommunicationchannelSet,AccountSet,SystemUserSet,ContactSet,optevia_interactionSet; do
    echo "Bark!" >&2
    sleep 1
done
