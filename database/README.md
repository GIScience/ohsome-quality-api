# Database

## Development

A quick database setup for development is provided utilizing Docker (`Dockerfile.production`) and SQL dumps from our production database covering selected regions. Please refer to [development setup documentation](docs/development-setup.md).


## Production

> Note: An internal documentation about our deployment of the production database exists in Confluence

Requirements:

- PostgreSQL 10.6
  - PostGIS 2.5
  - Extension:
    - postgis_raster
    - plpgsql
    - citext (hexadmin)
    - pgcrypt (hexadmin)
    - uuid-ossp (hexadmin)


The database schema is based on the ohsomehex database. Because of this the version of PostgreSQL and PostGIS are the same as of ohsomehex database.

In addition to the schema the ohsomehex isea relations (grid of hex cells) at zoom level 6 and 12 are used.

Please reach out to get SQL dumps containing both the ohsomehex schema and ohsomehex-isea relations if needed.


All other scripts for initializing the database can be found in the repository at `database/init_db.production/`.
The order of execution is defined in `database/init_db.production/init_db.sh`.

Execution time is about 3 hours.

Scripts to import additional datasets can be found at `database/scripts/import`. Those include the GlobalUrbanFootprint which is not part of the initial setup of the database due to size. The total size of GUF04 files are 32 GB. The total size of GUF04 table is 42 GB.
