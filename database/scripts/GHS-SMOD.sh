#!/bin/bash
# Execution time: 2,5 h

set -e

wget https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_SMOD_POP_GLOBE_R2019A/GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K/V2-0/GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.zip

unzip GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.zip

geotiff=GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif

psql --command \
    "DROP TABLE IF EXISTS ghs_smod"

raster2pgsql \
    -I \
    -M \
    -Y \
    -c \
    -C \
    -t 100x100 \
    -s 54009 \
    $geotiff public.ghs_smod \
    | \
    psql \
        -v ON_ERROR_STOP=1 \
        -d $PGDATABASE \
        -U $PGUSER
