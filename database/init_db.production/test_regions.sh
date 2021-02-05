ogr2ogr -f "PostgreSQL" PG:"dbname=$PGDATABASE user=$PGUSER" "test_regions.geojson" -nln test_regions -append
