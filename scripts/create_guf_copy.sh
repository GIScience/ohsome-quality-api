PGPASSWORD=6uPBpYXxpNTznB90FMrd7TiWM psql -h localhost -p 9000 -d pop -U read_only_user -c "\copy (SELECT * FROM guf04 WHERE rast && ST_MakeEnvelope(8.625,49.3711,8.7334,49.4397,4326)) TO 'guf-heidelberg.copy';"

PGPASSWORD=6uPBpYXxpNTznB90FMrd7TiWM psql -h localhost -p 9000 -d pop -U read_only_user -c "\copy (SELECT * FROM guf04 WHERE rast && ST_MakeEnvelope( 29.327168,-11.745695,40.445137,-0.985788,4326)) TO 'guf-tanzania.copy';"
