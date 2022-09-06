# Configuration

OQT can be configured using a configuration file or environment variables. Configuration
values from environment variables have precedence over values from the configuration
file.

Below is a table listing all possible configuration variables.

| Configuration Variable Name | Environment Variable Name     | Configuration File Name   | Default Value                                       | Description                                                                  |
| --------------------------- | -------------------------     | -----------------------   | --------------------------------------------------- | ---------------------------------------------------------------------------- |
| Postgres Host               | `POSTGRES_HOST`               | `postgres_host`           | `localhost`                                         | Database connection parameter                                                |
| Postgres Port               | `POSTGRES_PORT`               | `postgres_port`           | `5445`                                              | "                                                                            |
| Postgres Database           | `POSTGRES_DB`                 | `postgres_db`             | `oqt`                                               | "                                                                            |
| Postgres User               | `POSTGRES_USER`               | `postgres_user`           | `oqt`                                               | "                                                                            |
| Postgres Password           | `POSTGRES_PASSWORD`           | `postgres_password`       | `oqt`                                               | "                                                                            |
| Configuration File Path     | `OQT_CONFIG`                  | -                         | `workers/config/config.yaml`                        | Absolute path to the configuration file                                      |
| Data Directory              | `OQT_DATA_DIR`                | `data_dir`                | `data/`                                             | Absolute path to the directory for raster files                              |
| Datasets and Features IDs   | -                             | `datasets`                | `[{"regions": {"default": "ogc_fid"}}]`             | Dataset and Features Ids available in the database (see description below)   |
| Geometry Size Limit (km²)   | `OQT_GEOM_SIZE_LIMIT`         | `geom_size_limit`         | `100`                                               | Area restriction of the input geometry to the OQT API (sqkm)                 |
| Python Log Level            | `OQT_LOG_LEVEL`               | `log_level`               | `INFO`                                              | Python logging level                                                         |
| Concurrent Computations     | `OQT_CONCURRENT_COMPUTATIONS` | `concurrent_computations` | `4`                                                 | Limit number of concurrent Indicator computations for one API request        |
| User Agent                  | `OQT_USER_AGENT`              | `user_agent`              | `ohsome-quality-analyst/{version}`                  | User-Agent header for requests tot the ohsome API                            |
| ohsome API URL              | `OQT_OHSOME_API`              | `ohsome_api`              | `https://api.ohsome.org/v1/`                        | ohsome API URL                                                               |

_Note on the 'Datasets and Features IDs' configuration:_ Defines the datasets and
features IDs which are available in the database and for which Indicators should be
calculated. The `dataset` field refers to the name of the relation and `default` and
`other` refer to possible identifier of the features. The default configuration looks
like this:

```yaml
datasets:
    regions:
        default: ogc_fid
        other: [name] # Optional
```

## Configuration File

The default path of the configuration file is `workers/config/config.yaml`.
A sample configuration file can be found in the same directory: `workers/config/sample.config.yaml`.
All configuration files in this directory (`config`) will be ignored by Git. To change the default configuration file path for OQT set the environment variable `OQT_CONFIG` to the desired path.

To create a new configuration file simply copy the sample configuration file and change the values.

```
cp sample.config.yaml config.yaml
```
