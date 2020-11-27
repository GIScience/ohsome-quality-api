#!/bin/bash
set -e

wget https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_MT_GLOBE_R2019A/GHS_POP_E2015_GLOBE_R2019A_4326_9ss/V1-0/GHS_POP_E2015_GLOBE_R2019A_4326_9ss_V1_0.zip

unzip GHS_POP_E2015_GLOBE_R2019A_4326_9ss_V1_0

geotiff=GHS_POP_E2015_GLOBE_R2019A_4326_9ss_V1_0.tif

raster2pgsql \
    -I \
    -M \
    -Y \
    -c \
    -C \
    -t 100x100 \
    -s 954009 \
    $geotiff public.ghs_pop \
    | \
    psql \
        -v ON_ERROR_STOP=1
        -h localhost \
        -p 5432 \
        -d hexadmin \
        -U $POSTGRES_USER
