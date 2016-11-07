FROM python:3.5

ADD . /src
WORKDIR /src
RUN pip install -r requirements.txt
RUN pip install ipdb

EXPOSE 8080
