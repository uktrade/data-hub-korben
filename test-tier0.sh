#!/bin/bash -xe
py.test -vv --tb=short test/tier0 --cov=korben && \
    wget -O codecov.sh https://codecov.io/bash && \
    bash codecov.sh -t ${CODECOV_TOKEN}
