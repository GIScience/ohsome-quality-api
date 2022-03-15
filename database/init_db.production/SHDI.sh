#!/bin/bash
# Human Development Indices
# https://globaldatalab.org/shdi/shapefiles/
wget -U oqt https://globaldatalab.org/assets/2020/03/GDL%20Shapefiles%20V4.zip
unzip "GDL Shapefiles V4.zip"
shp2pgsql -d -s 4326 GDL\ Shapefiles\ V4.shp shdi | psql
psql -f SHDI.sql
