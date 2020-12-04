#!/bin/bash
#
# Script to import whole Global Urban Footprint (0.4 arc seconds) into database
# Note: This will take several days to complete.
#
# '2>> guf04.log':
# The standard error stream will be redirected to the file only, it will not be visible in the terminal. If the file already exists, the new data will get appended to the end of the file.

i=0
for filename in data/GUF04_v2/*.tif; do
    if [[ $i -eq 0 ]]; then
        # Create raster table and import first geotiff.
        # gdal_calc.py -A $filename --outfile=guf04.tif --calc="1*(A==255)" --NoDataValue=0
        gdalbuildvrt -vrtnodata "0 128" guf04.vrt $filename

        raster2pgsql \
            -c \
            -t 100x100 \
            -s 4326 \
            guf04.vrt \
            public.guf04 \
            2>> guf04.log \
            | \
            PGPASSWORD=mypassword psql \
            -h localhost \
            -p 5445 \
            -U hexadmin \
            -d hexadmin \
            2>> guf04.log
    fi

    # gdal_calc.py -A $filename --outfile=guf04.tif --calc="1*(A==255)" --NoDataValue=0
    gdalbuildvrt -vrtnodata "0 128" guf04.vrt $filename

    # Append geotiff to existing raster table
    raster2pgsql \
        -a \
        -t 100x100 \
        -s 4326 \
        guf04.vrt \
        public.guf04 \
        2>> guf04.log \
        | \
        PGPASSWORD=mypassword psql \
        -h localhost \
        -p 5445 \
        -U hexadmin \
        -d hexadmin \
        2>> guf04.log

    ((i++))
    echo -e "\n$i: $filename\n" >> guf04.log
done

# Create Index
# Add Raster Constraints
# Vacum Analyze
PGPASSWORD=mypassword psql \
    -h localhost \
    -p 5445 \
    -U hexadmin \
    -d hexadmin \
    -f GUF04_v2.sql
