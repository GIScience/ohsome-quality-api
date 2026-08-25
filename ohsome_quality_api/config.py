"""Load configuration from environment variables or configuration file on disk."""

import os
from types import MappingProxyType

import yaml

from ohsome_quality_api import __version__
from ohsome_quality_api.utils.helper import get_project_root


def get_config_path() -> str:
    """Get configuration file path

    Read value of the environment variable 'OQAPI_CONFIG' or use default 'config.yaml'
    """
    default = str(get_project_root() / "config" / "config.yaml")
    return os.getenv("OQAPI_CONFIG", default=default)


def load_config_default() -> dict:
    return {
        "ohsome_api_url": "https://ohsome-api.heigitk8s.de",
        "postgres_host": "localhost",
        "postgres_port": 5445,
        "postgres_db": "oqapi",
        "postgres_user": "oqapi",
        "postgres_password": "oqapi",
        "root_path": "",
        "swagger_css_url": "/static/swagger-ui.css",
        "swagger_js_url": "/static/swagger-ui-bundle.js",
        "data_dir": get_default_data_dir(),
        "geom_size_limit": 1000,
        "log_level": "INFO",
        "ohsome_api": "https://api.ohsome.org/v1/",
        "concurrent_computations": 4,
        "user_agent": "ohsome-quality-api/{}".format(__version__),
        "heigit_api_key": "foo",
        "datasets": {
            "regions": {
                "default": "ogc_fid",
                "other": ["name"],
            }
        },
    }


def load_config_from_file(path: str) -> dict:
    """Load configuration from file on disk."""
    if os.path.isfile(path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    else:
        return {}


def load_config_from_env() -> dict:
    """Load configuration from environment variables."""
    cfg = {
        "ohsome_api_url": os.getenv("OHSOME_API_URL"),
        "postgres_host": os.getenv("POSTGRES_HOST"),
        "postgres_port": os.getenv("POSTGRES_PORT"),
        "postgres_db": os.getenv("POSTGRES_DB"),
        "postgres_user": os.getenv("POSTGRES_USER"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD"),
        "root_path": os.getenv("ROOT_PATH"),
        "swagger_css_url": os.getenv("SWAGGER_CSS_URL"),
        "swagger_js_url": os.getenv("SWAGGER_JS_URL"),
        "data_dir": os.getenv("OQAPI_DATA_DIR"),
        "geom_size_limit": os.getenv("OQAPI_GEOM_SIZE_LIMIT"),
        "ohsome_api": os.getenv("OQAPI_OHSOME_API"),
        "concurrent_computations": os.getenv("OQAPI_CONCURRENT_COMPUTATIONS"),
        "user_agent": os.getenv("OQAPI_USER_AGENT"),
        "heigit_api_key": os.getenv("OQAPI_HEIGIT_API_KEY"),
    }
    return {k: v for k, v in cfg.items() if v is not None}


def get_config() -> MappingProxyType:
    """Get configuration variables from environment and file.

    Configuration values from file will be given precedence over default vaules.
    Configuration values from environment variables will be given precedence over file
    values.
    """
    cfg = load_config_default()
    cfg_file = load_config_from_file(get_config_path())
    cfg_env = load_config_from_env()
    cfg.update(cfg_file)
    cfg.update(cfg_env)
    return MappingProxyType(cfg)


def get_config_value(key: str) -> str | int | dict:
    config = get_config()
    return config[key]


def get_default_data_dir() -> str:
    return str(get_project_root() / "data")
