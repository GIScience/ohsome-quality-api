# Development Setup

To run all components (OQT/API, Database, Website) in Docker containers simply run:

```bash
docker-compose -f docker-compose.development.yml up -d
```

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

To access the database and the ohsome API various environment variables need to be set:

```bash
export OHSOME_API=https://api.ohsome.org/v1/
export POSTGRES_DB=oqt
export POSTGRES_USER=oqt
export POSTGRES_PASSWORD=mypassword
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_SCHEMA=public
```

> Tip: Above lines can be written to a file (E.g. `.env`) and sourced (`source .env`) to make them available to current environment.

Windows user can set those environment variables with following commands:

```
setx OHSOME_API https://api.ohsome.org/v1/
setx POSTGRES_DB oqt
setx POSTGRES_USER oqt
setx POSTGRES_PASSWORD mypassword
setx POSTGRES_HOST localhost
setx POSTGRES_PORT 5432
setx POSTGRES_SCHEMA public
```


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


