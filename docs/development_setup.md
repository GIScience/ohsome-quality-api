# Development Setup

To run all components (OQT/API, Database, Website) in Docker containers simply run:

```bash
docker-compose -f docker-compose.development.yml up -d
```

After all services are up they are available under:

- Website: [http://127.0.0.1:8081/](http://127.0.0.1:8081/)
- API: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- Database: `host=localhost port=5445 dbname=oqt user=oqt password=oqt`

Please continue reading for more information on each one of those services. If running into issues during the setup please check the [troubleshooting](/docs/troubleshooting.md) document. Also feel free to reach out to us.


## Database

A database for development purposes is provided as Dockerfile. This database contains custom regions, regions for running tests and datasets (SHDI and GHS-POP) for those regions. To build and run an already configured image run:

```bash
docker-compose -f docker-compose.development.yml up -d oqt-database
```

During building of the database Docker image data for development purposes is downloaded. When the database container is running for the first time it takes a few seconds until the database is initialized and ready to accept connections.
Check the progress with `docker logs oqt-database`.

To reinitialize or update the database make sure to delete the volume and rebuild the image. This will delete all data in the database:

```bash
# Make sure that your git is up2date, e.g. git pull
docker-compose -f docker-compose.development.yml down --remove-orphans --volumes
docker-compose -f docker-compose.development.yml up -d --force-recreate --build oqt-database
```

To avoid using the cache of Docker run:

```bash
docker-compose -f docker-compose.development.yml build --no-cache
docker-compose -f docker-compose.development.yml up -d
```

> If for development purposes additional datasets are required please have a look at the scripts found in the `database/init_db.production` directory. For example to import the GHS POP dataset simply run the provided script (`database/init_db.production/GHS_POP.sh`). This will delete the existing GHS POP table (which covers only the custom regions), download the GHS POP dataset and import it into the database.


### Database for running tests

A minimal database setup for running tests is provided. If the build argument `OQT_TEST_DB` is set to `True` a database is initialized with data only for the regions used by the tests. No (additional) data is downloaded as is the case with the database setup for development.


## Raster Datasets

Please refer to [/docs/raster_datasets.md](/docs/raster_datasets.md).


## OQT Python package


### Requirements

- Python: ≥ 3.8 and < 3.10
- Poetry: ≥ 1.1
- R: ≥ 4.0
- GDAL ≥ 3

This project uses [Poetry](https://python-poetry.org/docs/) for packaging and dependencies management. Please make sure it is installed on your system.


### Installation

```bash
cd workers/
poetry install
poetry shell  # Spawns a shell within the virtual environment.
pre-commit install  # Install pre-commit hooks.
# Hack away
```


### Configuration


#### Local database

For local development no additional configuration is required. Per default OQT will connect to the database defined in `docker-compose.development.yml`.


#### Remote database

If access to a remote database is required following environment variables need to be set:

```bash
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_SCHEMA
```

> Tip: Above lines can be written to a file (e.g. `.env`), prefixed with `export` and sourced (`source .env`) to make them available to current environment.
>
> Note: Windows user can set those environment variables with following command `setx POSTGRES_DB`


#### ohsome API

The URL to a specific ohsome API can be set with the environment variable `OHSOME_API`. It defaults to [https://api.ohsome.org/v1/](https://api.ohsome.org/v1/)


#### Additional options

Additional environment variables are:
- `OQT_LOG_LEVEL`: Control the logging level of OQT (See logging section)
- `OQT_GEOM_SIZE_LIMIT`: Control the size limit of the input geometry passed to the API.


### Usage


#### CLI

```bash
oqt --help
```


#### API


##### Start the API using Docker:

```bash
docker-compose -f docker-compose.development.yml up -d oqt-workers
```


##### Start the API using a Python script:

```bash
cd workers/scripts
python start_api.py
```

Default host is 127.0.0.1 and port is 8080. To change this, provide the corresponding parameter:

```bash
python start_api.py --help
Usage: start_api.py [OPTIONS]

Options:
  --host TEXT     [default: 127.0.0.1]
  --port INTEGER  [default: 8080]
  --help          Show this message and exit.
```


##### Endpoints

Go to [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs) and check out the endpoints.

Alternative query the API from a terminal using CURL:

```bash
# GET request for an indicator
curl \
    -X GET "http://127.0.0.1:8080/indicator/GhsPopComparisonBuildings?layerName=building_count&dataset=regions&featureId=1" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    | python -m json.tool > response.json


# POST request for a report
curl \
    -X POST "http://127.0.0.1:8080/report/SimpleReport" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d '{"dataset": "regions", "featureId": 1}' \
    | python -m json.tool > response.json
```


### Tests

All relevant components should be tested. Please write tests for newly integrated functionality. 

Tests are written using the [unittest library](https://docs.python.org/3/library/unittest.html).
The test runner is [pytest](https://docs.pytest.org/en/stable/).
Tests are separated into integration tests and unit tests.
Unit tests should run without having access to the database or services on the internet (e.g. ohsome API).

Run all tests:

```bash
cd workers/
pytest tests
```


#### Writing tests


##### VCR (videocassette recorder) for tests

All tests that are calling function, which are dependent on external resources (e.g. ohsome API) have to use the [VCR.py](https://vcrpy.readthedocs.io) module: "VCR.py records all HTTP interactions that take place […]."
This ensures that the positive test result is not dependent on the external resource. The cassettes are stored in the test directory within [fixtures/vcr_cassettes](/workers/tests/integrationtests/fixtures/vcr_cassettes). These cassettes are supposed to be integrated (committed and pushed) to the repository.

The VCR [record mode](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) is configurable through the environment variable `VCR_RECORD_MODE`. To ensure that every request is covered by cassettes, run the tests with the record mode `none`. If necessary, the cassettes can be re-recorded by deleting the cassettes and run all tests again, or using the record mode `all`. This is not necessary in normal cases, because not-yet-stored requests are downloaded automatically.

Writing tests using VCR.py with our custom decorator is as easy as: 

```python
from .utils import oqt_vcr

class TestSomething(unittest.TestCase):

    @oqt_vcr.use_cassette()
    def test_something(self):
        oqt.do_something(…)
        self.assertSomething(something)
```

Good examples can be found in [test_oqt.py](/workers/tests/integrationtests/test_oqt.py).


##### Asynchronous functions

When writing tests for functions which are asynchronous (using the `async/await` pattern) such as the `preprocess` functions of indicator classes, those functions should be called as follows: `asyncio.run(indicator.preprocess())`.


### Logging

Logging is enabled by default.

`ohsome_quality_analyst` uses the [logging module](https://docs.python.org/3/library/logging.html).
The module is configured in `definitions.py`.  Both entry-points to `ohsome_quality_analyst`, the `cli.py` and the `api.py`, will call the configuration function defined in `definitions.py`.
The default log level is `INFO`. This can be overwritten by setting the environment variable `OQT_LOG_LEVEL`.


#### Usage

```python
import logging

logging.info("Logging message")
```
