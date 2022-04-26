# Database

## Development

A quick database setup for development is provided utilizing Docker (`Dockerfile.production`) and SQL dumps from our production database covering selected regions. Please refer to the [development setup documentation](docs/development-setup.md).


## Production

Requirements:

- PostgreSQL 10.6
  - PostGIS 2.5
  - Extension:
    - plpgsql

Scripts for initializing the database can be found in the repository at `database/init_db.production/`.
The order of execution is defined in `database/init_db.production/init_db.sh`.
