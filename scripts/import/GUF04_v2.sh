#!/bin/bash
#
# '2>> error-guf04.txt':
# The standard error stream will be redirected to the file only, it will not be visible in the terminal. If the file already exists, the new data will get appended to the end of the file.

gdalbuildvrt -vrtnodata "0 128" guf04.vrt data/GUF04_v2/*.tif

raster2pgsql -c -M -I -C -t 100x100 -s 4326 data/GUF04_v2/guf04.vrt public.guf04 2>> error-guf04.txt | PGPASSWORD=mypassword psql -h localhost -p 5445 -U hexadmin -d hexadmin 2>> error-guf04.txt

psql -h localhost -p 5445 -U hexadmin -d hexadmin -c 'SELECT AddRasterConstraints('guf04'::name, 'rast'::name);' # AddRasterConstraints
