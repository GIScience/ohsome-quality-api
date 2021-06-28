#!/bin/bash
set -e

wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326.geojson
wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_60M_2021_4326.geojson

psql --command \
    "DROP TABLE IF EXISTS nuts_rg_01M_2021"
psql --command \
    "DROP TABLE IF EXISTS nuts_rg_60M_2021"

ogr2ogr -f PostgreSQL PG:"dbname=$PGDATABASE user=$PGUSER" -nln "nuts_rg_01M_2021" NUTS_RG_01M_2021_4326.geojson
ogr2ogr -f PostgreSQL PG:"dbname=$PGDATABASE user=$PGUSER" -nln "nuts_rg_60M_2021" NUTS_RG_60M_2021_4326.geojson

rm NUTS_RG_01M_2021_4326.geojson
rm NUTS_RG_60M_2021_4326.geojson
