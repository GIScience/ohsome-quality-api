# Development Setup

To run simply run the ohsome quality API and the database the provided Docker setup can be used.

```bash
docker compose up --detach
```

After all services are up they are available under:

- API: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- Database: `host=localhost port=5445 dbname=oqapi user=oqapi password=oqapi`

For development setup please continue reading.


## Requirements

- Python: ≥ 3.10
- Poetry: ≥ 1.5
- R: ≥ 4.0

This project uses [Poetry](https://python-poetry.org/docs/) for packaging and dependencies management. Please make sure it is installed on your system.

For development a database and raster datasets on disk might not be needed. In case the database is needed start the database service defined in the docker compose file. If raster datasets are needed please refer to [/docs/raster_datasets.md](/docs/raster_datasets.md) for setting those up.


## Installation

```bash
poetry install
poetry shell  # Spawns a shell within the virtual environment.
pre-commit install  # Install pre-commit hooks.
# Hack away
pytest  # Run all tests
```


## Configuration

For all possible configuration parameter please refer to the [configuration documentation](/docs/configuration.md).

For local development no custom configuration is required.


## Usage

```bash
python scripts/start_api.py
```

Go to [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs) and check out the endpoints.

Default host is 127.0.0.1 and port is 8080. To change this, provide the corresponding parameter:

```bash
$ cd scripts
$ python start_api.py --help
Usage: start_api.py [OPTIONS]

Options:
  --host TEXT     [default: 127.0.0.1]
  --port INTEGER  [default: 8080]
  --help          Show this message and exit.
```


## Tests

All relevant components should be tested. Please write tests for newly integrated
functionality.

The test framework is [pytest](https://docs.pytest.org/en/stable/).

To run all tests just execute `pytest`:

```bash
pytest
```

### VCR for Tests

All tests that are calling function, which are dependent on external resources (e.g. ohsome API) have to use the [VCR.py](https://vcrpy.readthedocs.io) module: "VCR.py records all HTTP interactions that take place […]."
This ensures that the positive test result is not dependent on the external resource. The cassettes are stored in the test directory within [fixtures/vcr_cassettes](/tests/integrationtests/fixtures/vcr_cassettes). These cassettes are supposed to be integrated (committed and pushed) to the repository.

The VCR [record mode](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) is configurable through the environment variable `VCR_RECORD_MODE`. To ensure that every request is covered by cassettes, run the tests with the record mode `none`. If necessary, the cassettes can be re-recorded by deleting the cassettes and run all tests again, or using the record mode `all`. This is not necessary in normal cases, because not-yet-stored requests are downloaded automatically.

Writing tests using VCR.py with our custom decorator is as easy as:

```python
from tests import oqapi_vcr


@oqapi_vcr.use_cassette
def test_something(self):
    oqapi.do_something(…)
```

Good examples can be found in [test_oqt.py](/tests/integrationtests/test_oqt.py).

### Asynchronous functions

When writing tests for functions which are asynchronous (using the `async/await` pattern) such as the `preprocess` functions of indicator classes, those functions should be called as follows: `asyncio.run(indicator.preprocess())`.

### Approval Tests

[Approval tests](https://approvaltests.com/resources/) capture the output
(snapshot) of a program and compares it with a previously approved version of
the output.

Its most useful in cases Agile development environments where frequent changes
are expected or where the output is of complex nature but can be easily
verified by humans aided by a diff-tool or visual representation of the output.

> A picture’s worth a 1000 tests.

Once the output has been *approved* then as long as the output stays the same
the test will pass. A test fails if the current output (*received*) is not
identical to the approved output. In this case, the difference of the received
and the approved output is reported. The representation of the report can take
any form, for example opening a diff-tool to compare received and approved
text or displaying an image. Thus, the test pattern is as follows:
`Arrange, Act, Print, Verify`.

A good introduction into approval tests gives [this video](https://www.youtube.com/watch?v=QEdpE0chA-s).

ohsome quality API uses approval tests to verify result descriptions.
For comparison its recommended to have a diff tool installed on your system
such as Meld or PyCharm. If changes in the code lead to a different output
approval tests will show the difference to the previously approved version of
the output using a diff tool. If it es as expected resolve the difference using
the diff-tool save and rerun the tests.

## Logging

Logging is enabled by default.

`ohsome_quality_api` uses the [logging module](https://docs.python.org/3/library/logging.html).

### Configuration

The logging module is configured in `config.py`. Both entry-points to
`ohsome_quality_api`, the `api.py`, will call the configuration
function defined in `definitions.py`. The default log level is `INFO`. This can be
overwritten by setting the environment variable `OQAPI_LOG_LEVEL` (See also the
[configuration documentation](docs/configuration.md)).

### Usage

```python
import logging

logging.info("Logging message")
```


## Database Library

[asyncpg](https://magicstack.github.io/asyncpg/current/) is used as database interface
library.

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
