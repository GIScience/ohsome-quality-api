# Configuration

The ohsome quality API can be configured using a configuration file or environment variables. Configuration
values from environment variables have precedence over values from the configuration
file.

Below is a table listing all possible configuration variables.

| Configuration Variable Name  | Environment Variable Name       | Configuration File Name        | Default Value                  | Description                                                                 |
| ---------------------------  | ------------------------------- | -------------------------      | ------------------------------ | --------------------------------------------------------------------------- |
| ohsomeDB Host                | `OHSOMEDB_HOST`                 | `ohsomedb_host`                | `localhost`                    | ohsomeDB database connection parameter                                      |
| ohsomeDB Port                | `OHSOMEDB_PORT`                 | `ohsomedb_port`                | `5432`                         | "                                                                           |
| ohsomeDB Database            | `OHSOMEDB_DB`                   | `ohsomedb_db`                  | `postgres`                     | "                                                                           |
| ohsomeDB User                | `OHSOMEDB_USER`                 | `ohsomedb_user`                | `postgres`                     | "                                                                           |
| ohsomeDB Password            | `OHSOMEDB_PASSWORD`             | `ohsomedb_password`            | `mylocalpassword`              | "                                                                           |
| ohsomeDB Contributions Table | `OHSOMEDB_CONTRIBUTIONS_TABLE`  | `ohsomedb_contributions_table` | `contributions`                | "                                                                           |
| Postgres Host                | `POSTGRES_HOST`                 | `postgres_host`                | `localhost`                    | Postgres database connection parameter                                      |
| Postgres Port                | `POSTGRES_PORT`                 | `postgres_port`                | `5445`                         | "                                                                           |
| Postgres Database            | `POSTGRES_DB`                   | `postgres_db`                  | `oqapi`                        | "                                                                           |
| Postgres User                | `POSTGRES_USER`                 | `postgres_user`                | `oqapi`                        | "                                                                           |
| Postgres Password            | `POSTGRES_PASSWORD`             | `postgres_password`            | `oqapi`                        | "                                                                           |
| Configuration File Path      | `OQAPI_CONFIG`                  | -                              | `config/config.yaml`           | Absolute path to the configuration file                                     |
| Geometry Size Limit (km²)    | `OQAPI_GEOM_SIZE_LIMIT`         | `geom_size_limit`              | `1000`                         | Area restriction of the input geometry                                      |
| Python Log Level             | `OQAPI_LOG_LEVEL`               | `log_level`                    | `INFO`                         | Python logging level                                                        |
| Concurrent Computations      | `OQAPI_CONCURRENT_COMPUTATIONS` | `concurrent_computations`      | `4`                            | Limit number of concurrent Indicator computations for one API request       |
| User Agent                   | `OQAPI_USER_AGENT`              | `user_agent`                   | `ohsome-quality-api/{version}` | User-Agent header for requests tot the ohsome API                           |
| ohsome API URL               | `OQAPI_OHSOME_API`              | `ohsome_api`                   | `https://api.ohsome.org/v1/`   | ohsome API URL                                                              |


## Configuration File

The default path of the configuration file is `config/config.yaml`.
A sample configuration file can be found in the same directory: `config/sample.config.yaml`.
All configuration files in this directory (`config`) will be ignored by Git. To change the default configuration file path set the environment variable `OQAPI_CONFIG` to the desired path.

To create a new configuration file simply copy the sample configuration file and change the values.

```
cd config/
cp sample.config.yaml config.yaml
```
