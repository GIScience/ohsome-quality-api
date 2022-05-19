# Development

How-to informations for developers working on the `ohsome-quality-analyst` Python
project.

## Logging

Logging is enabled by default.

`ohsome_quality_analyst` uses the [logging module](https://docs.python.org/3/library/logging.html).
The module is configured in `definitions.py`. Both entry-points to OQT, the `cli.py` and
the `api.py`, will call the configuration function defined in `definitions.py`. The
default log level is `INFO`. This can be overwritten by setting the environment variable
`OQT_LOG_LEVEL`.

### Usage

```python
import logging

logging.info("Logging message")
```


## Tests

All relevant components should be tested. Please write tests for newly integrated
functionality.

Tests are written using the
[unittest library](https://docs.python.org/3/library/unittest.html).
The test runner is [pytest](https://docs.pytest.org/en/stable/). Tests are separated
into integration tests and unit tests. Unit tests should run without having access to
the database or services on the internet (e.g. ohsome API).

To run all tests:

```bash
cd workers/
pytest tests
```

### Writing tests

#### VCR (videocassette recorder) for tests

All tests that are calling functions, which are dependent on external resources over
HTTP (e.g. ohsome API) have to use the [VCR.py](https://vcrpy.readthedocs.io) module:
"VCR.py records all HTTP interactions that take place […]." This ensures that the
positive test result is not dependent on the external resource. The cassettes are stored
in the test directory within
[fixtures/vcr_cassettes](/workers/tests/integrationtests/fixtures/vcr_cassettes). These
cassettes are supposed to be integrated (committed and pushed) to the repository.

The VCR [record mode](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) is
configurable through the environment variable `VCR_RECORD_MODE`. To ensure that every
request is covered by cassettes, run the tests with the record mode `none`. If
necessary, the cassettes can be re-recorded by deleting the cassettes and run all tests
again, or using the record mode `all`. This is not necessary in normal cases, because
not-yet-stored requests are downloaded automatically.

Writing tests using VCR.py with our custom decorator is as easy as:

```python
from .utils import oqt_vcr

class TestSomething(unittest.TestCase):

    @oqt_vcr.use_cassette()
    def test_something(self):
        oqt.do_something(…)
        self.assertSomething(something)
```

Good examples can be found in 
[test_oqt.py](/workers/tests/integrationtests/test_oqt.py).

#### Asynchronous functions

When writing tests for functions which are asynchronous (using the `async/await`
pattern) such as the `preprocess` functions of indicator classes, those functions should
be called as follows: `asyncio.run(indicator.preprocess())`.


## Database

OQT uses [asyncpg](https://magicstack.github.io/asyncpg/current/) as database interface
library.

### executemany query

In Psycopg one can execute a query for each element of a list with
`executemany(insert_query, vars_list)`.

To archive similar result in `asyncpg` one would write a SQL query which takes an array
as input:

```python
await conn.fetch('''
    INSERT INTO people (name) (SELECT unnest ($1))
    RETURNING id
''', ['anne', 'ben', 'charlie'])
```
