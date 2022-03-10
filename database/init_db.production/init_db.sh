# ohsome-hex-isea.sql is not included in repository due to file size.
# Execution time: ~ 3h (2,5h for GHS_POP)

export POSTGRES_DB=oqt
export POSTGRES_HOST=
export POSTGRES_PASSWORD=
export POSTGRES_PORT=
export POSTGRES_SCHEMA=public
export POSTGRES_USER=oqt

psql -f admin-schema.sql
psql -f ohsome-hex-isea.sql
./NUTS_2021.sh
./GADM.sh
psql -f GADM.sql
./GHS_POP.sh
./SHDI.sh
psql -f regions.sql
