# Configuration

The ohsome quality API can be configured using a configuration file or environment variables. Configuration
values from environment variables have precedence over values from the configuration
file.

Required configuration variables are:

| Configuration Variable Name  | Environment Variable Name       | Configuration File Name        | Default Value                  | Description                                                                 |
| ---------------------------  | ------------------------------- | -------------------------      | ------------------------------ | --------------------------------------------------------------------------- |
| Postgres Host                | `POSTGRES_HOST`                 | `postgres_host`                | `localhost`                    | Postgres database connection parameter                                      |
| Postgres Port                | `POSTGRES_PORT`                 | `postgres_port`                | `5445`                         | "                                                                           |
| Postgres Database            | `POSTGRES_DB`                   | `postgres_db`                  | `oqapi`                        | "                                                                           |
| Postgres User                | `POSTGRES_USER`                 | `postgres_user`                | `oqapi`                        | "                                                                           |
| Postgres Password            | `POSTGRES_PASSWORD`             | `postgres_password`            | `oqapi`                        | "                                                                           |

For a list of all possible configuration variables please take a look at the [`config/sample.config.yaml](/config/sample.config.yaml) or [ohsome-quality-api/config.py](/ohsome-quality-api/config.py)

## Configuration File

The default path of the configuration file is `config/config.yaml`.
A sample configuration file can be found in the same directory: `config/sample.config.yaml`.
All configuration files in this directory (`config`) will be ignored by Git. To change the default configuration file path set the environment variable `OQAPI_CONFIG` to the desired path.

To create a new configuration file simply copy the sample configuration file and change the values.

```
cd config/
cp sample.config.yaml config.yaml
```
