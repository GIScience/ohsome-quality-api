#!/bin/bash
set -e

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_gpkg.zip
unzip gadm36_gpkg.zip

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_levels_gpkg.zip
unzip gadm36_levels_gpkg.zip

ogr2ogr -f PostgreSQL "PG:dbname=hexadmin user=$POSTGRES_USER host=localhost port=5432 password=$POSTGRES_PASSWORD" gadm36.gpkg
ogr2ogr -f PostgreSQL "PG:dbname=hexadmin user=$POSTGRES_USER host=localhost port=5432 password=$POSTGRES_PASSWORD" gadm36_levels.gpkg

rm gadm36*
