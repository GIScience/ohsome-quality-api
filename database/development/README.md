# Development Database

## Database for Development

A minimal database setup for development is provided utilizing Docker and SQL dumps from
the production database, which will be downloaded during building of the image.

For more details please refer to the
[development setup documentation](docs/development-setup.md).

## Database for Running Tests

If the build argument `OQT_TEST_DB` is set to `True` a database is initialized with data
only for the regions used by the tests. No (additional) data is downloaded as is the
case with the database setup for development.
