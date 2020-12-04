#!/bin/bash

cd data
# Extract extent (bbox) from ogrinfo
# Bbox format: lon1 lat1 lon2 lat2
bbox_comma="$(ogrinfo -al -so Dar-Es-Salaam.geojson | grep Extent | awk -v ORS="," -v RS=")" -v FS="(" '{print $2}' | sed -r 's/,/ /g' | xargs | sed -r 's/ /,/g')"
bbox="$(echo $bbox_comma | sed 's/,/ /g')"
echo "Bounding Box: $bbox"
echo $bbox > bbox.txt
echo -e "Done!\n"

bbox_formatted=$(echo $bbox | sed 's/ /,/g')
outfile="Dar-Es-Salaam.tif"
gdal_translate \
    -sds \
    -of GTiff PG:"host=localhost port=5432 dbname=pop user=read_only_user password=6uPBpYXxpNTznB90FMrd7TiWM schema=public table=guf04 where='rast && ST_MakeEnvelope($bbox_formatted, 4326)' mode='2'" \
    $outfile

raster2pgsql \
    -I \
    -M \
    -Y \
    -c \
    -C \
    -t 100x100 \
    -s 4326 \
    $outfile public.guf04_daressalaam\
    | \
    PGPASSWORD=mypassword psql \
    -h localhost \
    -p 5445 \
    -d hexadmin \
    -U hexadmin
