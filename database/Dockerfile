FROM postgis/postgis:15-3.3

# Initialization scripts.
ADD --chmod=644 https://downloads.ohsome.org/oqapi/COPYRIGHTS.md \
    https://downloads.ohsome.org/oqapi/shdi.sql.gz \
    https://downloads.ohsome.org/oqapi/hexcells.sql.gz \
    /docker-entrypoint-initdb.d/
