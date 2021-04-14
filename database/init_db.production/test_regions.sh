psql --command \
    "DROP TABLE IF EXISTS test_regions"
# nln: Assign an alternate name to the new layer
# nlt: Define the geometry type for the created layer
# lco: Layer creation option (format specific)
ogr2ogr \
    -f PostgreSQL PG:"
        host=$POSTGRES_HOST
        port=$POSTGRES_PORT
        dbname=$POSTGRES_DB
        user=$POSTGRES_USER
        password=$POSTGRES_PASSWORD
        "\
    "test_regions.geojson" \
    -nln test_regions\
    -nlt MULTIPOLYGON\
    -lco GEOMETRY_NAME=geom
