FROM python:3.5

ADD actual-requirements.txt /src/actual-requirements.txt
RUN pip install -r /src/actual-requirements.txt
RUN pip install ipdb
ADD . /src
WORKDIR /src
RUN pip install -e .

EXPOSE 8080
