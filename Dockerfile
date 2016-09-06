FROM python

ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
RUN pip install ipdb
ADD . /src
WORKDIR /src
RUN python setup.py install

ADD staging.yml /src/config.yml
ENV KORBEN_CONF_PATH=/src/config.yml
