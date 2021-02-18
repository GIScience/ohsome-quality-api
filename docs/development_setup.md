# Development Setup

## Requirements

This project uses [Poetry](https://python-poetry.org/docs/) for packaging and dependencies management.
Please make sure it is installed on your system.


## Installation

```bash
cd workers/
poetry install
poetry shell  # Spawns a shell within the virtual environment.
pre-commit install  # Install pre-commit hooks.
# Hack away
```

> Note: If during the installation of `matplotlib` an error occurs the solution could be to install `freetype`. See the install documentation of `matplotlib`: https://github.com/matplotlib/matplotlib/blob/master/INSTALL.rst#freetype-and-qhull


## Database

To get access to a running database on a remote server please reach out.

To access the Database and to specify ohsome API URL various environment variables need to be set.
To do this create a `.env` file at the root of the repository and write down following variables and their values:

```bash
OHSOME_API=https://api.ohsome.org/v1/
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hexadmin
POSTGRES_USER=hexadmin
POSTGRES_SCHEMA=public
POSTGRES_PASSWORD=mypassword
```

To make the variables available to current environment run following command (Linux):

```
export $(cat .env | xargs)
```

Windows user can set those environment variables manually with following commands:

```
setx OHSOME_API https://api.ohsome.org/v1/
setx POSTGRES_HOST localhost
setx POSTGRES_PORT 5432
setx POSTGRES_DB hexadmin
setx POSTGRES_USER hexadmin
setx POSTGRES_SCHEMA public
setx POSTGRES_PASSWORD mypassword
```

> Another possibility is to setup a database for development locally. This is still work in progress. Please refer to this issue on GitLab for questions and progress regarding local development database: https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-analyst/-/issues/48


## Usage

CLI:
```
oqt --help
```

API:
```
uvicorn ohsome_quality_analyst.api:app --reload
```

Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and check out the endpoints.
