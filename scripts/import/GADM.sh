#!/bin/bash

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_gpkg.zip
unzip gadm36_gpkg.zip

wget https://biogeo.ucdavis.edu/data/gadm3.6/gadm36_levels_gpkg.zip
unzip gadm36_levels_gpkg.zip

ogr2ogr -f PostgreSQL "PG:dbname=hexadmin user=hexadmin host=129.206.228.76 port=5445 password=mypassword" gadm36.gpkg
ogr2ogr -f PostgreSQL "PG:dbname=hexadmin user=hexadmin host=129.206.228.76 port=5445 password=mypassword" gadm36_levels.gpkg

PGPASSWORD=mypassword psql -h localhost -p 5445 -d hexadmin -U hexadmin -f GADM.sql

rm gadm36*
