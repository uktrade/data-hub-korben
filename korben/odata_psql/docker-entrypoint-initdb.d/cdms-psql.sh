#!/bin/bash
set -e

export LANGUAGE="en_GB.UTF-8"
export LANG="en_GB.UTF-8"
export LC_ALL="en_GB.UTF-8"

psql -v ON_ERROR_STOP=1 -d "$POSTGRES_DB" --username "$POSTGRES_USER" -f /cdms-psql-create.sql
