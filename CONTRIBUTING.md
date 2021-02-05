# Contributing

Please contribute to this repository through [merge requests](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html#new-merge-request-from-your-local-environment).


## Setup

### Requirements

This project uses [Poetry](https://python-poetry.org/docs/) for packaging and dependencies management.
Please make sure it is installed on your system.


### Installation

```bash
poetry install
poetry shell  # Spawns a shell within the virtual environment.
pre-commit install  # Install pre-commit hooks.
# Hack away ...
```

> Note: If during the installation of `matplotlib` an error occurs the solution could be to install `freetype`. See the install documentation of `matplotlib`: https://github.com/matplotlib/matplotlib/blob/master/INSTALL.rst#freetype-and-qhull


### Database

To get access to a running database on a remote server please reach out.

To access the Database and to specify ohsome API URL various environment variables need to be set.
To do this create a `.env` file at the root of the repository and write down following variables and their values:

```bash
OHSOME_API=https://api.ohsome.org/v1/
POSTGRES_DB=hexadmin
POSTGRES_USER=hexadmin
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_PASSWORD=mypassword
POSTGRES_SCHEMA=public
```

To make the variables available to current environment run following command (Linux):

```
export $(cat .env | xargs)
```

Windows user can set those environment variables manually with following commands:

```
setx POSTGRES_PASSWORD mypassword
setx POSTGRES_HOST localhost
setx POSTGRES_PORT 5432
setx POSTGRES_SCHEMA public
```

> Another possibility is to setup a database for development locally. This is still work in progress. Please refer to this issue on GitLab for questions and progress regarding local development database: https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-tool/-/issues/48


## Usage

### OQT

```
oqt --help
```

### API

```
uvicorn ohsome_quality_tool.api:app --reload
```

Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and check out the endpoints.



## Style Guide

This project uses [black](https://github.com/psf/black), [flake8](https://gitlab.com/pycqa/flake8) and [isort](https://github.com/PyCQA/isort) to ensure consistent codestyle. Those tools should already be installed in your virtual environment since they are dependencies definied in the `pyproject.toml` file.

The configuration of flake8 and isort is stored in `setup.cfg`.

In addition [pre-commit](https://pre-commit.com/) is setup to run those tools prior to any git commit.

> Tip 1: Ignore a hook: `SKIP=flake8 git commit -m "foo"`
>
> Tip 2: Mark in-line that flake8 should not raise any error: `print()  # noqa`


## Tests

Please provide tests.

```bash
# Run a single test:
python -m unittest tests/test_indicator_mapping_saturation.py

# Run all test:
python -m unittest discover
```


## Troubleshooting

Please refer to [docs/troubleshooting.md](docs/troubleshooting.md)
