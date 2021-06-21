# Human Development Indices (5.0)
# https://globaldatalab.org/shdi/shapefiles/

wget https://globaldatalab.org/assets/2020/03/GDL%20Shapefiles%20V4.zip

unzip "GDL Shapefiles V4.zip"

shapefile="GDL Shapefiles V4.shp"

psql --command \
    "DROP TABLE IF EXISTS hdi"

ogr2ogr -f "PostgreSQL" PG:"dbname=$PGDATABASE user=$PGUSER" $shapefile public.hdi
# -skip-failures
