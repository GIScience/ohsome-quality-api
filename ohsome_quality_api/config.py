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
        "postgres_host": "localhost",
        "postgres_port": 5445,
        "postgres_db": "oqapi",
        "postgres_user": "oqapi",
        "postgres_password": "oqapi",
        "ohsome_api_url": "https://ohsome-api.heigitk8s.de",
        "heigit_api_key": "",
        "user_agent": "ohsome-quality-api/{}".format(__version__),
        "root_path": "",
        "docs_url": None,
        "log_level": "INFO",
        "concurrent_computations": 4,
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
        "postgres_host": os.getenv("POSTGRES_HOST"),
        "postgres_port": os.getenv("POSTGRES_PORT"),
        "postgres_db": os.getenv("POSTGRES_DB"),
        "postgres_user": os.getenv("POSTGRES_USER"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD"),
        "ohsome_api_url": os.getenv("OHSOME_API_URL"),
        "heigit_api_key": os.getenv("OQAPI_HEIGIT_API_KEY"),
        "user_agent": os.getenv("OQAPI_USER_AGENT"),
        "root_path": os.getenv("ROOT_PATH"),
        "docs_url": os.getenv("OQAPI_DOCS_URL"),
        "concurrent_computations": os.getenv("OQAPI_CONCURRENT_COMPUTATIONS"),
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


def get_config_value(key: str) -> str | int | dict | None:
    config = get_config()
    return config[key]
