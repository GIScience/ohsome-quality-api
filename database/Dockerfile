# Use the official image as a parent image.
FROM postgis/postgis:13-3.0

# Initialization scripts
# https://github.com/docker-library/docs/blob/master/postgres/README.md#initialization-scripts
COPY ohsome-hex-isea.sql /docker-entrypoint-initdb.d
