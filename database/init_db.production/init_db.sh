export POSTGRES_DB=oqt
export POSTGRES_HOST=
export POSTGRES_PASSWORD=
export POSTGRES_PORT=
export POSTGRES_SCHEMA=public
export POSTGRES_USER=oqt

./NUTS_2021.sh
./GADM.sh
psql -f GADM.sql
./SHDI.sh
psql -f regions.sql
