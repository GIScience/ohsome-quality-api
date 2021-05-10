# Development Setup

To run all components (OQT/API, Database, Website) in Docker containers simply run:

```bash
docker-compose -f docker-compose.development.yml up -d
```

After all services are up they are available under:

- Website: [http://127.0.0.1:8081/](http://127.0.0.1:8081/)
- API: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- Database: `host=localhost port=5445 dbname=oqt user=oqt password=oqt`

Please continue reading for more information on each one of those services. If running into issues during the setup please check the [troubleshooting](docs/troubleshooting.md) document. Also feel free to reach out to us.


## Database

A database for development purposes is provided as Dockerfile. To build and run an already configured image run:

```bash
docker-compose -f docker-compose.development.yml up -d oqt-database
```

When the database container is running for the first time it takes a couple of minutes until the database is initialized and ready to accept connections.
Check the progress with `docker logs oqt-database`.

To reinitialize or update the database make sure to delete the volume and rebuild the image. This will delete all data in the database:

```bash
# Make sure that your git is up2date, e.g. git pull
docker stop oqt-database && docker rm oqt-database
docker volume rm ohsome-quality-analyst_oqt-dev-pg_data
docker-compose -f docker-compose.development.yml up -d --build oqt-database
```

> If for development purposes additional datasets are required have a look at the [database/README.md](database/README.md). On this page information about various scripts for data import are provided. E.g. if the GHS population dataset is needed, first delete the `ghs_pop` table (which covers only the test regions) from the development database and then use the provided script (`database/init_db.production/GHS_POP.sh`) to import the whole dataset.


## OQT Python package

### Requirements

- Python 3.8+
- Poetry 1.1.0+

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

> Note: Windows user can set those environment variables with following command `setx POSTGRES_DB`

#### ohsome API

The URL to a specific ohsome API can be set with the environment variable `OHSOME_API`. It defaults to [https://api.ohsome.org/v1/](https://api.ohsome.org/v1/)

#### Misc

Additional environment variables are:
- `OQT_LOG_LEVEL`: Control the logging level of OQT (See logging section)
- `OQT_GEOM_SIZE_LIMIT`: Control the size limit of the input geometry passed to the API.


### Usage

#### CLI

```bash
oqt --help
```

#### API

Start the API using Docker:

```bash
docker-compose -f docker-compose.development.yml up -d oqt-workers
```

Start the API using a Python script:

```bash
cd workers/
python run_uvicorn.py  # Default host is 127.0.0.1 and port is 8080
python start_api.py --help

Usage: start_api.py [OPTIONS]

Options:
  --host TEXT
  --port INTEGER
  --help          Show this message and exit.
```

Go to [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs) and check out the endpoints.

Alternative query the API from a terminal using CURL:

```bash
# GET request for an indicator
curl -X GET "http://127.0.0.1:8080/indicator/GhsPopComparison?layerName=building_count&dataset=test_regions&featureId=1" | python -m json.tool > response.json

# POST request for a report
curl -X POST "http://127.0.0.1:8080/report/SimpleReport" -d '{"dataset": "test_regions", "featureId": 1}' | python -m json.tool > response.json
```


### Tests

Tests are written using the [unittest library](https://docs.python.org/3/library/unittest.html).
The test runner is [pytest](https://docs.pytest.org/en/stable/).
Tests are separated into integration tests and unit tests.
Unit tests should run without having access to the database or services on the internet (e.g. ohsome API).

```bash
cd workers/
pytest tests
```


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
