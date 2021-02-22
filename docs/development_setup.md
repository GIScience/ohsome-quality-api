# Development Setup

To run all components (OQT/API, Database, Website) in Docker containers simply run:

```bash
docker-compose -f docker-compose.development.yml up -d
```

After all services are up they are available under:

- Website: [http://127.0.0.1:8081/](http://127.0.0.1:8081/)
- API: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- Database: `host=localhost port=5445 dbname=oqt user=oqt password=oqt`


## OQT Python package

### Requirements

This project uses [Poetry](https://python-poetry.org/docs/) for packaging and dependencies management.
Please make sure it is installed on your system.


### Installation

```bash
cd workers/
poetry install
poetry shell  # Spawns a shell within the virtual environment.
pre-commit install  # Install pre-commit hooks.
# Hack away
```

> Note: If during the installation of `matplotlib` an error occurs the solution could be to install `freetype`. See the install documentation of `matplotlib`: https://github.com/matplotlib/matplotlib/blob/master/INSTALL.rst#freetype-and-qhull


### Configuration

**Local database:**

For local development no additional configuration is required. Per default OQT will connect to the database definied in `docker-compose.development.yml`.

**Remote database:**

If access to a remote database is required following environment variables need to be set:

```bash
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_SCHEMA
```

> Tip: Above lines can be written to a file (E.g. `.env`), prefixed with `export` and sourced (`source .env`) to make them available to current environment.

Windows user can set those environment variables with following command `setx POSTGRES_DB`


**ohsome API:**

The URL to a specific ohsome API can be set with the environment variable `OHSOME_API`. It defaults to [https://api.ohsome.org/v1/](https://api.ohsome.org/v1/)


### Usage

CLI:
```bash
oqt --help
```

API:
```bash
uvicorn ohsome_quality_analyst.api:app --reload
```

Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and check out the endpoints.


## Database

A database for development purposes is provided as Dockerfile. To build and run a already configured image run:

```bash
docker-compose -f docker-compose.development.yml up -d oqt-database
```

To get access to a running database on a remote server please reach out.


