FROM postgis/postgis:15-3.3

RUN  apt-get update \
  && apt-get install -y wget gzip \
  && rm -rf /var/lib/apt/lists/*

# Initialization scripts.
RUN wget https://downloads.ohsome.org/OQT/COPYRIGHTS.md
RUN wget https://downloads.ohsome.org/OQT/shdi.sql.gz
RUN wget https://downloads.ohsome.org/OQT/hexcells.sql.gz
RUN gunzip shdi.sql.gz
RUN gunzip hexcells.sql.gz
RUN mv shdi.sql /docker-entrypoint-initdb.d/
RUN mv hexcells.sql /docker-entrypoint-initdb.d/
