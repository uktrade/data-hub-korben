FROM python:3.5

ADD actual-requirements.txt actual-requirements.txt
RUN pip install -r actual-requirements.txt
ADD . /src
WORKDIR /src
RUN pip install -e .
RUN pip install ipdb

EXPOSE 8080
