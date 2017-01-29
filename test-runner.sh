#!/bin/bash -xe
SUITE=$1

py.test -vv --tb=short $SUITE --cov=korben
if [ "$CI" = "true" ] && [ "$CIRCLECI" = "true" ];
then
    wget -O codecov.sh https://codecov.io/bash
    bash codecov.sh
fi
