> WARNING: This is not used in production and is experimental only. It can be used to setup a "full" database locally which is similar to the database in production. 

> NOTE: The Postgres version differs from the version used in the development setup.

# Production Database

```bash
docker build -t oqt-database .
docker run -e POSTGRES_PASSWORD=oqt -e POSTGRES_USER=oqt -p 5432:5432 oqt-database
```
