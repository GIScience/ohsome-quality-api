#!/bin/bash
set -e

mkdir -p /tmp
cd /tmp

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_gpkg.zip
unzip gadm36_gpkg.zip

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_levels_gpkg.zip
unzip gadm36_levels_gpkg.zip

ogr2ogr -f PostgreSQL "PG:dbname=hexadmin user=$POSTGRES_USER" gadm36.gpkg
ogr2ogr -f PostgreSQL "PG:dbname=hexadmin user=$POSTGRES_USER" gadm36_levels.gpkg

rm gadm36*
