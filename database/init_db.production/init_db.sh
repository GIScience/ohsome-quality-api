export $(cat .env | xargs)

# Substitude hardcoded postgres role "hexadmin" with $PGUSER
# sed -i "s/hexadmin/${PGUSER}/g" admin-schema
# sed -i "s/hexadmin/${$PGUSER}/g" ohsome-hex-isea.sql

psql -f admin-schema.sql
psql -f ohsome-hex-isea.sql
./NUTS_2021.sh
./GADM.sh
psql -f GADM.sql
./GHS_POP.sh
./test_regions.sh
