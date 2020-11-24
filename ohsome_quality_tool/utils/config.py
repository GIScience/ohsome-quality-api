import logging.config
import os
from pathlib import Path

from xdg import XDG_DATA_HOME

# get Postgres config from environment
POSTGRES_DB = os.getenv("POSTGRES_DB", default="oqt")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", default="oqt_workers")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", default="development")

# get ohsome api endpoint from environment
OHSOME_API = os.getenv("OHSOME_API", default="https://api.ohsome.org/v1/")

# define logging file path and config
DATA_PATH = os.path.join(XDG_DATA_HOME, "ohsome_quality_tool")
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)
LOGGING_FILE_PATH = os.path.join(DATA_PATH, "oqt.log")
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"  # noqa: E501
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "standard",
            "filename": LOGGING_FILE_PATH,
            "when": "D",
            "interval": 1,
            "backupCount": 14,
        },
    },
    "loggers": {
        "root": {"handlers": ["console"], "level": "INFO"},
        "oqt": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("oqt")
