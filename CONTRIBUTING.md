# Contributing

## Development Setup

This project uses [Poetry](https://python-poetry.org/) for packaging and dependencies management.
Please make sure it is installed on your system.

```bash
poetry install
poetry shell  # Spawns a shell within the virtual environment.
pre-commit install  # Install pre-commit hooks.
# Hack away ...
```

- To add dependencies: `poetry add package-name`
- To update dependencies: `poetry update package-name`


## Style Guide

This project uses [black](https://github.com/psf/black), [flake8](https://gitlab.com/pycqa/flake8), [isort](https://github.com/PyCQA/isort) and [mypy](http://www.mypy-lang.org/) to ensure consistent code.

The configuration of flake8 and isort is stored in `setup.cfg`.

[pre-commit](https://pre-commit.com/) is setup to run those tools prior to any git commit.
Those tools should already be installed in your virtual environment since they are listed in `requirements.txt`.
To setup pre-commit simply run:

```bash
pre-commit install
```

> Tip 1: Ignore a hook: `SKIP=flake8 git commit -m "foo"`
>
> Tip 2: Mark inline that flake8 should not raise any error: `print()  # noqa`
