FROM postgis/postgis:15-3.3

# Initialization scripts.
ADD --chmod=644 https://downloads.ohsome.org/OQT/COPYRIGHTS.md \
    https://downloads.ohsome.org/OQT/shdi.sql.gz \
    https://downloads.ohsome.org/OQT/hexcells.sql.gz \
    /docker-entrypoint-initdb.d/
