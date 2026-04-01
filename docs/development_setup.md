# Development Setup

Run the ohsome quality API as Docker container:

```bash
docker compose up --detach
```
After the ohsome quality API service is up the API documentation is served to [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs).

For development setup please continue reading.

## Requirements

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/): ≥ 0.7
- R: ≥ 4.0

This project uses [`uv`](https://docs.astral.sh/uv/getting-started/installation/) for package and project management. Please make sure it is installed on your system.


## Installation

```bash
uv sync
uv run prek install  # pre-commit hooks
uv run pybabel compile -d ohsome_quality_api/locale
```

### Building fails with CompileError

In case of a CompileError (see below) try running `CC=gcc uv sync`.

```
Resolved 85 packages in 33ms
  × Failed to build `rpy2==3.5.17`
  ├─▶ The build backend returned an error
  ╰─▶ Call to `setuptools.build_meta.build_wheel` failed (exit status: 1)
      [...]
      distutils.compilers.C.errors.CompileError: command 'clang' failed: No such file or directory
```


## ohsomeDB

For some experimental development work a local setup of the ohsomeDB is needed.
Currently, ohsomeDB is under active development.
You can find up-to-date setup instruction on [HeiGIT's GitLab](https://gitlab.heigit.org/giscience/big-data/ohsome/ohsomedb/ohsomedb/-/tree/main/local_setup).
If you run a local ohsomeDB make sure to set the appropriate configuration variables (see next section).


## Configuration

For all possible configuration parameter please refer to the [configuration documentation](/docs/configuration.md).

For local development no custom configuration is required, except for the work on indicators which need access to our database.


## Usage

```bash
uv run fastapi dev ohsome_quality_api/api/api.py
```


## Tests

All relevant components should be tested. Please write tests for newly integrated functionality.

The test framework is [pytest](https://docs.pytest.org/en/stable/).

To run all tests just execute `pytest`:

```bash
uv run pytest
```

To run them all in parallel execute `pytest -n auto`:

```bash
uv run pytest -n auto
```

To run tests with log level DEBUG:

```bash
OQAPI_LOG_LEVEL=DEBGU uv run pytest
```

### VCR for Tests

All tests that are calling function, which are dependent on external network resources (e.g. ohsome API) have to use the [VCR.py](https://vcrpy.readthedocs.io) module: "VCR.py records all HTTP interactions that take place […]."

The cassettes are stored in the test directory within [fixtures/vcr_cassettes](/tests/integrationtests/fixtures/vcr_cassettes). These cassettes are supposed to be integrated (committed and pushed) to the repository.

The VCR [record mode](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) is configurable through the environment variable `VCR_RECORD_MODE`. To ensure that every request is covered by cassettes, run the tests with the record mode `none`. If necessary, the cassettes can be re-recorded by deleting the cassettes and run all tests again, or using the record mode `all`. This is not necessary in normal cases, because not-yet-stored requests are downloaded automatically.

Writing tests using VCR.py with our custom decorator is as easy as:

```python
from tests import oqapi_vcr


@oqapi_vcr.use_cassette
def test_something(self):
    oqapi.do_something(…)
```

Good examples can be found in [test_main.py](/tests/integrationtests/test_main.py).

### Asynchronous functions

To test asynchronous functions (`async/await` pattern) use following pytest mark:

```python
@pytest.mark.asyncio
@oqapi_vcr.use_cassette
def test_something(self):
    await oqapi.do_something(…)
```

### Approval Tests

`ohsome-quality-api` uses approval/snapshot testing to verify among other
things indicator result description and figures. To read more about approval
tests read the [about section](https://github.com/GIScience/pytest-approval?tab=readme-ov-file#about)
of `pytest-approval`, the library which `ohsome-quality-api` uses.

### Regression Tests

Unlike the above-mentioned unit and integration tests,
regression tests do not primarily serve to guide and validate the development,
but to check if an upcoming version caused bugs in the existing system.

The regression tests are implemented in `hurl`
and can be run manually on the command line against any of the staging systems.
Please consider adding new `hurl` tests if you add new endpoints.
A `hurl` plugin for JetBrains IDEs (e.g. PyCharm, Intellij Idea etc.)
is available for syntax highlighting and execution within the IDE.

For details, check the [regression test README](../regression-tests/README.md).

## Logging

The default log level is `INFO`.
This can be overwritten by setting the environment variable `OQAPI_LOG_LEVEL`.

### Usage

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Logging message")
```


## Database Library

[asyncpg](https://magicstack.github.io/asyncpg/current/) is used as database client library.

### `executemany` Query

In Psycopg one can execute a query for each element of a list with
`executemany(insert_query, vars_list)`.

To achieve similar results in `asyncpg`, one would write an SQL query which takes an array
as input:

```python
await conn.fetch('''
    INSERT INTO people (name) (SELECT unnest ($1))
    RETURNING id
''', ['anne', 'ben', 'charlie'])
```


## Notes on the integration of R

The package [`rpy2`](https://rpy2.github.io/) is utilized to execute R code.

> `rpy2` is an interface to R running embedded in a Python process.

For an example how the ohsome quality API is using `rpy2` have a look the module [`models.py`](/ohsome_quality_api/indicators/mapping_saturation/models.py).
Through this module the Mapping Saturation indicator uses some of the built-in statistical models of R.
