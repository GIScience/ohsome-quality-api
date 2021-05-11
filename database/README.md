# Database

## Development

A quick database setup for development is provided utilizing Docker (`Dockerfile.production`) and SQL dumps from our production database covering selected regions. Please refer to the [development setup documentation](docs/development-setup.md).


## Production

Requirements:

- PostgreSQL 10.6
  - PostGIS 2.5
  - Extension:
    - postgis_raster
    - plpgsql
    - citext (hexadmin)
    - pgcrypt (hexadmin)
    - uuid-ossp (hexadmin)


The database schema is based on the ohsomehex database. Because of this the version of PostgreSQL and PostGIS are the same as of ohsomehex database. In addition to the schema the ohsomehex isea relations (grid of hex cells) at zoom level 6 and 12 are used. Please reach out to get SQL dumps containing both the ohsomehex schema and ohsomehex-isea relations if needed.

All other scripts for initializing the database can be found in the repository at `database/init_db.production/`.
The order of execution is defined in `database/init_db.production/init_db.sh`.

Execution time is about 3 hours.
