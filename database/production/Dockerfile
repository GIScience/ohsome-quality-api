FROM postgis/postgis:14-3.2

RUN  apt-get update \
  && apt-get install -y wget gzip \
  && rm -rf /var/lib/apt/lists/*

# Copy script for index creation
COPY create-index.sql /docker-entrypoint-initdb.d/2-create-index.sql

# Get postgres dump
RUN wget \
  --output-document /docker-entrypoint-initdb.d/1-dump.sql.gz \
  https://downloads.ohsome.org/OQT/dump.sql.gz
RUN cd /docker-entrypoint-initdb.d/ \
  && gzip -d 1-dump.sql.gz
