# Contributing

## Development Setup

## Virtual Environment and Dependency Management 

This project uses [Poetry](https://python-poetry.org/docs/) for packaging and dependencies management.
Please make sure it is installed on your system.

```bash
poetry install
poetry shell  # Spawns a shell within the virtual environment.
pre-commit install  # Install pre-commit hooks.
# Hack away ...
```

- To add dependencies: `poetry add package-name`
- To update dependencies: `poetry update package-name`

### MacOS
When installing matplotlib freetype needed to be installed on the system level. Run: `brew install freetype`

## Environment Variables for accessing Database

To access the Database various environment variables need to be set.
To do this create a `.env` file at the root of the repository and write down following variables and their values:

```bash
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=hexadmin
POSTGRES_USER=hexadmin
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

To make the variables available to current environment run following command:

```
export $(cat .env | xargs)
```

Set up a local postgis database using docker:
* run `docker-compose up -d oqt-postgres`
* it will take around 15 minutes until all layers are set up
* you can check the progress of the setup in the logs `docker logs oqt-postgres`
* once you get `database system is ready to accept connections` in the logs the import was successful


## Style Guide

This project uses [black](https://github.com/psf/black), [flake8](https://gitlab.com/pycqa/flake8), [isort](https://github.com/PyCQA/isort) and [mypy](http://www.mypy-lang.org/) to ensure consistent code. Those tools should already be installed in your virtual environment since they are dependencies definied in the `pyproject.toml` file.

The configuration of flake8 and isort is stored in `setup.cfg`.

Each of those tools can be integrated in most editors.

In addition [pre-commit](https://pre-commit.com/) is setup to run those tools prior to any git commit.
To setup pre-commit simply run:

```bash
pre-commit install
```

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
