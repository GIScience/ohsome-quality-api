#!/bin/bash
#
# '2>> error-guf04.txt':
# The standard error stream will be redirected to the file only, it will not be visible in the terminal. If the file already exists, the new data will get appended to the end of the file.

raster2pgsql -c -M -I -t 100x100 -s 4326 *.tif public.guf04 2>> error-guf04.txt | psql -U postgres -d pop 2>> error-guf04.txt

psql -U postgres -d pop -c 'SELECT AddRasterConstraints('guf04'::name, 'rast'::name);' # AddRasterConstraints
