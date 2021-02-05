#!/bin/bash
set -e

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_gpkg.zip
unzip gadm36_gpkg.zip

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_levels_gpkg.zip
unzip gadm36_levels_gpkg.zip

ogr2ogr -f PostgreSQL "PG:dbname=$PGDATABASE user=$PGUSER" gadm36.gpkg
ogr2ogr -f PostgreSQL "PG:dbname=$PGDATABASE user=$PGUSER" gadm36_levels.gpkg

rm gadm36*
