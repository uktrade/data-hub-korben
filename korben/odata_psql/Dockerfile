FROM ubuntu

# explicitly set user/group IDs
RUN groupadd -r postgres --gid=999
RUN useradd -r -g postgres --uid=999 postgres

# Custom PostgreSQL compilation
RUN apt-get update -y
RUN apt-get install -y libbison-dev git build-essential gzip \
    libreadline-dev zlib1g-dev flex
RUN mkdir -p /tmp/build
WORKDIR /tmp/build
RUN git clone https://github.com/postgres/postgres.git
ADD namedatalen.patch /tmp/build
WORKDIR /tmp/build/postgres
RUN git checkout "REL9_5_3"
RUN git apply ../namedatalen.patch
RUN ./configure
RUN make
RUN make install

RUN apt-get install -y gosu

ENV PATH /usr/local/pgsql/bin/:$PATH
ENV PGDATA /var/lib/postgresql/data
ENV POSTGRES_DB cdms_psql

VOLUME /var/lib/postgresql/data


WORKDIR /
RUN locale-gen en_GB.UTF-8
RUN update-locale LANG=en_GB.UTF-8 LANGUAGE=en_GB.UTF-8 LC_ALL=en_GB.UTF-8
ADD docker-entrypoint.sh /
RUN chmod a+x docker-entrypoint.sh

ADD docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
ADD cdms-psql-create.sql /cdms-psql-create.sql


ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
