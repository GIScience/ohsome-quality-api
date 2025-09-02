"""Load configuration from environment variables or configuration file on disk."""

import logging
import logging.config
import os
import sys
from types import MappingProxyType

import rpy2.rinterface_lib.callbacks
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
        "ohsomedb_host": "localhost",
        "ohsomedb_port": 5432,
        "ohsomedb_db": "postgres",
        "ohsomedb_user": "postgres",
        "ohsomedb_password": "mylocalpassword",
        "postgres_host": "localhost",
        "postgres_port": 5445,
        "postgres_db": "oqapi",
        "postgres_user": "oqapi",
        "postgres_password": "oqapi",
        "data_dir": get_default_data_dir(),
        "geom_size_limit": 1000,
        "log_level": "INFO",
        "ohsome_api": "https://api.ohsome.org/v1/",
        "concurrent_computations": 4,
        "user_agent": "ohsome-quality-api/{}".format(__version__),
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
        "ohsomedb_host": os.getenv("OHSOMEDB_HOST"),
        "ohsomedb_port": os.getenv("OHSOMEDB_PORT"),
        "ohsomedb_db": os.getenv("OHSOMEDB_DB"),
        "ohsomedb_user": os.getenv("OHSOMEDB_USER"),
        "ohsomedb_password": os.getenv("OHSOMEDB_PASSWORD"),
        "postgres_host": os.getenv("POSTGRES_HOST"),
        "postgres_port": os.getenv("POSTGRES_PORT"),
        "postgres_db": os.getenv("POSTGRES_DB"),
        "postgres_user": os.getenv("POSTGRES_USER"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD"),
        "data_dir": os.getenv("OQAPI_DATA_DIR"),
        "geom_size_limit": os.getenv("OQAPI_GEOM_SIZE_LIMIT"),
        "ohsome_api": os.getenv("OQAPI_OHSOME_API"),
        "concurrent_computations": os.getenv("OQAPI_CONCURRENT_COMPUTATIONS"),
        "user_agent": os.getenv("OQAPI_USER_AGENT"),
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


def load_logging_config():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"  # noqa
            }
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"handlers": ["default"], "level": "INFO"},
    }
    level = get_log_level()
    config["root"]["level"] = getattr(logging, level.upper())
    return config


def get_log_level():
    if "pydevd" in sys.modules or "pdb" in sys.modules:
        default_level = "DEBUG"
    else:
        default_level = "INFO"
    return os.getenv("OQAPI_LOG_LEVEL", default=default_level)


def configure_logging() -> None:
    """Configure logging level and format."""

    class RPY2LoggingFilter(logging.Filter):  # Sensitive
        def filter(self, record):
            return " library ‘/usr/share/R/library’ contains no packages" in record.msg

    # Avoid R library contains no packages WARNING logs.
    # OQAPI has no dependencies on additional R libraries.
    rpy2.rinterface_lib.callbacks.logger.addFilter(RPY2LoggingFilter())
    # Avoid a huge amount of DEBUG logs from matplotlib font_manager.py
    logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)
    logging.config.dictConfig(load_logging_config())
