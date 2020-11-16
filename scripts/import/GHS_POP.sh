#!/bin/bash
#
# http://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_MT_GLOBE_R2019A/GHS_POP_E2015_GLOBE_R2019A_54009_250/V1-0/GHS_POP_E2015_GLOBE_R2019A_54009_250_V1_0.zip
#
# '2>> error-guf04.txt':
# The standard error stream will be redirected to the file only, it will not be visible in the terminal. If the file already exists, the new data will get appended to the end of the file.

geotiff=data/GHS_POP/GHS_POP_E2015_GLOBE_R2019A_54009_250_V1_0.tif

raster2pgsql \
    -I \
    -M \
    -Y \
    -c \
    -t 100x100 \
    -s 954009 \
    $geotiff public.ghspop \
    2>> error-ghspop.log \
    | \
    psql \
        -h localhost \
        -p 5432 \
        -d hexadmin \
        -U hexadmin \
        2>> error-ghspop.log

psql \
    -h localhost \
    -p 5432 \
    -d hexadmin \
    -U hexadmin \
    -c "SELECT AddRasterConstraints('public.ghspop'::name, 'rast'::name);" \
    2>> error-ghspop.log
