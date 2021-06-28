#!/bin/bash
# Human Development Indices (5.0)
# https://globaldatalab.org/shdi/shapefiles/

# Download from https://globaldatalab.org/assets/2020/03/GDL%20Shapefiles%20V4.zip

unzip "GDL Shapefiles V4.zip"

mv "GDL Shapefiles V4.dbf" "GDL-Shapefiles-V4.dbf"
mv "GDL Shapefiles V4.prj" "GDL-Shapefiles-V4.prj"
mv "GDL Shapefiles V4.shp" "GDL-Shapefiles-V4.shp"
mv "GDL Shapefiles V4.shx" "GDL-Shapefiles-V4.shx"

shapefile='GDL-Shapefiles-V4.shp'

psql --command \
    "DROP TABLE IF EXISTS shdi"

ogr2ogr -f "PostgreSQL" PG:"dbname=$PGDATABASE user=$PGUSER" -nln public.shdi -nlt PROMOTE_TO_MULTI $shapefile 

rm "GDL-Shapefiles-V4.dbf"
rm "GDL-Shapefiles-V4.prj"
rm "GDL-Shapefiles-V4.shp"
rm "GDL-Shapefiles-V4.shx"
