FROM python

ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
ADD . /src
WORKDIR /src
RUN python setup.py install
