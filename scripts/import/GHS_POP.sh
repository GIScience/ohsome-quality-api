#!/bin/bash
#
# http://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_MT_GLOBE_R2019A/GHS_POP_E2015_GLOBE_R2019A_54009_250/V1-0/GHS_POP_E2015_GLOBE_R2019A_54009_250_V1_0.zip
#
# '2>> error.txt':
# The standard error stream will be redirected to the file only, it will not be visible in the terminal. If the file already exists, the new data will get appended to the end of the file.

geotiff=GHS_POP_E2015_GLOBE_R2019A_54009_250_V1_0.tif

psql \
    -h localhost \
    -p 5432 \
    -d hexadmin \
    -U hexadmin \
    -c "INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 954009, 'esri', 54009, '+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ', 'PROJCS["World_Mollweide",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Mollweide"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",0],UNIT["Meter",1],AUTHORITY["EPSG","54009"]]');"
    2>> error-ghs_pop.log

raster2pgsql \
    -I \
    -M \
    -Y \
    -c \
    -t 100x100 \
    -s 954009 \
    $geotiff public.ghs_pop \
    2>> error-ghs_pop.log \
    | \
    psql \
        -h localhost \
        -p 5432 \
        -d hexadmin \
        -U hexadmin \
        2>> error-ghs_pop.log

psql \
    -h localhost \
    -p 5432 \
    -d hexadmin \
    -U hexadmin \
    -c "SELECT AddRasterConstraints('public.ghs_pop'::name, 'rast'::name);" \
    2>> error-ghs_pop.log
