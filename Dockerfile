FROM python

ADD . /src
WORKDIR /src
RUN python setup.py install
