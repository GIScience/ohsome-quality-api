ogr2ogr \
    -f PostgreSQL PG:"host=$POSTGRES_HOST password=$POSTGRES_PASSWORD\
    dbname=$POSTGRES_DB user=$POSTGRES_USER" \
    "test_regions.geojson" \
    -nln test_regions\
    -lco GEOMETRY_NAME=geom
