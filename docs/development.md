# Development

Information for developers working on the `ohsome-quality-analyst` project.

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

The test framework is [pytest](https://docs.pytest.org/en/stable/).

To run all tests:

```bash
cd workers/
pytest
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

@oqt_vcr.use_cassette
def test_something(self):
    oqt.do_something(…)
```

Good examples can be found in 
[test_oqt.py](/workers/tests/integrationtests/test_oqt.py).

#### Asynchronous functions

When writing tests for functions which are asynchronous (using the `async`/`await`
pattern), such as the `preprocess` functions of indicator classes, these functions should
be called as follows: `asyncio.run(indicator.preprocess())`.


## Database

OQT uses [asyncpg](https://magicstack.github.io/asyncpg/current/) as database interface
library.

### executemany query

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
