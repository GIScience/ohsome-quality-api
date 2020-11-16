wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326.geojson
wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_60M_2021_4326.geojson

ogr2ogr -f "PostgreSQL" PG:"dbname=ohsome-hex user=hexadmin" "NUTS_RG_01M_2021_4326.geojson"
ogr2ogr -f "PostgreSQL" PG:"dbname=ohsome-hex user=hexadmin" "NUTS_RG_60M_2021_4326.geojson"
