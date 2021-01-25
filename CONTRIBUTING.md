# Contributing


Please contribute to this repository through pull requests.

https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html#new-merge-request-from-your-local-environment


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

Another possiblity is to setup a database for development localy. This is still work in progress. Please refer to this issue on GitLab for questions and progress regarding local development database: https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-tool/-/issues/48

* run `docker-compose up -d oqt-database`
* it will take around 15 minutes until all layers are set up
* you can check the progress of the setup in the logs `docker logs oqt-database`
* once you get `database system is ready to accept connections` in the logs the import was successful


To access the Database various environment variables need to be set.
To do this create a `.env` file at the root of the repository and write down following variables and their values:

```bash
POSTGRES_PASSWORD=mypassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_SCHEMA=public
```

To make the variables available to current environment run following command:

```
export $(cat .env | xargs)
```
For Windows you can set the variables in the command line as following:
```
setx POSTGRES_PASSWORD mypassword
setx POSTGRES_HOST localhost
setx POSTGRES_PORT 5432
setx POSTGRES_SCHEMA public
```
(Caution: They are now global)

## Style Guide

This project uses [black](https://github.com/psf/black), [flake8](https://gitlab.com/pycqa/flake8) and [isort](https://github.com/PyCQA/isort) to ensure consistent codestyle. Those tools should already be installed in your virtual environment since they are dependencies definied in the `pyproject.toml` file.

The configuration of flake8 and isort is stored in `setup.cfg`.

In addition [pre-commit](https://pre-commit.com/) is setup to run those tools prior to any git commit.

> Tip 1: Ignore a hook: `SKIP=flake8 git commit -m "foo"`
>
> Tip 2: Mark inline that flake8 should not raise any error: `print()  # noqa`


## Tests

For each indicator and each report there should be a test in place. Ideally there will be several tests per indicator or report, e.g. a test for the dynamic processing and the another test for the static processing.

During development you should use the tests to check if your code changes didn't break any existing functionality.

You can run all tests like this:
```
python -m unittest discover tests/
```

When working on a specific part of the project it will be often enough to run a test for a single indicator or report. Use this line if you want to run only a specific test:

```
python -m unittest tests/test_indicator_mapping_saturation.py
```
