# Use the official image as a parent image.
FROM postgis/postgis:10-3.0

# Initialization scripts
# https://github.com/docker-library/docs/blob/master/postgres/README.md#initialization-scripts
COPY postgis-raster.sql /docker-entrypoint-initdb.d/1.sql
COPY admin-schema.sql /docker-entrypoint-initdb.d/2.sql
COPY ohsome-hex-isea.sql /docker-entrypoint-initdb.d/3.sql
