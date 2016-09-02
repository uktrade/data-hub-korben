FROM ubuntu

# Custom PostgreSQL compilation
RUN apt-get update -y
# libbison-dev gzip git build-essential libreadline-dev zlib1g-dev
RUN apt-get install -y  postgresql-server-dev-all libbison-dev git build-essential gzip libreadline-dev zlib1g-dev flex
RUN apt-get remove -y postgresql-server-dev-all
RUN mkdir -p /tmp/build
WORKDIR /tmp/build
RUN git clone https://github.com/postgres/postgres.git
ADD . /tmp/build
WORKDIR /tmp/build/postgres
RUN git checkout "REL9_5_3"
RUN git apply ../namedatelen.patch
RUN ./configure
RUN make
RUN make install

RUN chmod a+x /tmp/build/start.sh
CMD start.sh
