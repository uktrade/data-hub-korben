FROM python:3.5

ADD actual-requirements.txt /src/actual-requirements.txt
RUN pip install -r /src/actual-requirements.txt
RUN pip install ipdb
ADD . /src
WORKDIR /src
RUN pip install -e .

# Install dockerize https://github.com/jwilder/dockerize
RUN apt-get update && apt-get install -y wget

ENV DOCKERIZE_VERSION v0.3.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz


EXPOSE 8080
