"""Load configuration from environment variables or configuration file on disk."""

import logging
import logging.config
import os
import sys
from types import MappingProxyType
from typing import Union

import rpy2.rinterface_lib.callbacks
import yaml

from ohsome_quality_analyst import __version__ as oqt_version


def get_config_path() -> str:
    """Get configuration file path

    Read value of the environment variable 'OQT_CONFIG' or use default 'config.yaml'
    """
    return os.getenv(
        "OQT_CONFIG",
        default=os.path.abspath(
            os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__),
                ),
                "..",
                "config",
                "config.yaml",
            ),
        ),
    )


def load_config_default() -> dict:
    return {
        "postgres_host": "localhost",
        "postgres_port": 5445,
        "postgres_db": "oqt",
        "postgres_user": "oqt",
        "postgres_password": "oqt",
        "data_dir": get_default_data_dir(),
        "geom_size_limit": 100,
        "log_level": "INFO",
        "ohsome_api": "https://api.ohsome.org/v1/",
        "concurrent_computations": 4,
        "user_agent": "ohsome-quality-analyst/{}".format(oqt_version),
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
        "data_dir": os.getenv("OQT_DATA_DIR"),
        "geom_size_limit": os.getenv("OQT_GEOM_SIZE_LIMIT"),
        "ohsome_api": os.getenv("OQT_OHSOME_API"),
        "concurrent_computations": os.getenv("OQT_CONCURRENT_COMPUTATIONS"),
        "user_agent": os.getenv("OQT_USER_AGENT"),
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


def get_config_value(key: str) -> Union[str, int, dict]:
    config = get_config()
    return config[key]


def get_default_data_dir() -> str:
    """Get the default OQT data directory path.

    Default data directory is a directory named 'data' at the root of the repository.
    """
    return os.path.join(
        os.path.dirname(
            os.path.abspath(__file__),
        ),
        "..",
        "data",
    )


def load_logging_config():
    """Read logging configuration from configuration file."""
    path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__),
        ),
        "..",
        "config",
        "logging.yaml",
    )
    level = get_log_level()
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    config["root"]["level"] = getattr(logging, level.upper())
    return config


def get_log_level():
    if "pydevd" in sys.modules or "pdb" in sys.modules:
        default_level = "DEBUG"
    else:
        default_level = "INFO"
    return os.getenv("OQT_LOG_LEVEL", default=default_level)


def configure_logging() -> None:
    """Configure logging level and format."""

    class RPY2LoggingFilter(logging.Filter):  # Sensitive
        def filter(self, record):
            return " library ‘/usr/share/R/library’ contains no packages" in record.msg

    # Avoid R library contains no packages WARNING logs.
    # OQT has no dependencies on additional R libraries.
    rpy2.rinterface_lib.callbacks.logger.addFilter(RPY2LoggingFilter())
    # Avoid a huge amount of DEBUG logs from matplotlib font_manager.py
    logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)
    logging.config.dictConfig(load_logging_config())
