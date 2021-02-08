# ohsome-hex-isea.sql is not included in repository due to file size.
# Execution time: ~ 3h (2,5h for GHS_POP)

export POSTGRES_DB=
export POSTGRES_HOST=
export POSTGRES_PASSWORD=
export POSTGRES_PORT=
export POSTGRES_SCHEMA=public
export POSTGRES_USER=

# Substitude hardcoded postgres role "hexadmin" with $PGUSER
sed -i "s/hexadmin/${PGUSER}/g" admin-schema.sql
sed -i "s/hexadmin/${$PGUSER}/g" ohsome-hex-isea.sql

psql -f admin-schema.sql
psql -f ohsome-hex-isea.sql
./NUTS_2021.sh
./GADM.sh
psql -f GADM.sql
./GHS_POP.sh
./test_regions.sh
