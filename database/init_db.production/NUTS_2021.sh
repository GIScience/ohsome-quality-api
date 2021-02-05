#!/bin/bash
set -e

mkdir -p /tmp
cd /tmp

wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326.geojson
wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_60M_2021_4326.geojson

ogr2ogr -f PostgreSQL PG:"dbname=$POSTGRES_DB user=$POSTGRES_USER" -nln "nuts_rg_60M_2021" NUTS_RG_01M_2021_4326.geojson
ogr2ogr -f PostgreSQL PG:"dbname=$POSTGRES_DB user=$POSTGRES_USER" -nln "nuts_rg_60M_2021" NUTS_RG_60M_2021_4326.geojson

rm NUTS_RG_01M_2021_4326.geojson
rm NUTS_RG_60M_2021_4326.geojson
