FROM python:3.5

ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
RUN pip install ipdb
ADD . /src
WORKDIR /src
RUN python setup.py install

EXPOSE 8080
