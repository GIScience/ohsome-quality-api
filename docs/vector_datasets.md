# Vector datasets (PostGIS Database)

OQT operates on vector datasets stored in a PostGIS database.


## Setup

Missing in this document are dataset: NUTS, GADM and GHS-POP.

NUTS and GADM will probably be removed in the future: https://github.com/GIScience/ohsome-quality-analyst/issues/165

GHS-POP in the database will be replaced by a raster file stored on disk.


### The Human Development Index (SHDI)

Information:
- https://globaldatalab.org/shdi/
- product: GDL Shapefiles V4, epoch: 1990–2017, resolution: Subnational, coordinate system: EPSG:4326

Setup steps:
- Run provided import script: [database/scripts/import/SHDI.sh](database/scripts/import/SHDI.sh)
