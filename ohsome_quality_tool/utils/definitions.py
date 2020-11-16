import logging.config
import os
from enum import Enum, unique
from pathlib import Path

from xdg import XDG_DATA_HOME


# TODO: Is there a better way to define this?
@unique
class Indicators(Enum):
    """Define supported indicators."""

    BUILDING_COMPLETENESS = 1
    POI_DENSITY = 2
    LAST_EDIT = 3

    @property
    def constructor(self):
        from ohsome_quality_tool.indicators.building_completeness.indicator import (
            Indicator as buildingCompletenessIndicator,
        )
        from ohsome_quality_tool.indicators.last_edit.indicator import (
            Indicator as lastEditIndicator,
        )
        from ohsome_quality_tool.indicators.poi_density.indicator import (
            Indicator as poiDensityIndicator,
        )

        indicators = {
            1: buildingCompletenessIndicator,
            2: poiDensityIndicator,
            3: lastEditIndicator,
        }

        return indicators[self.value]


# TODO: Is there a better way to define this?
class Reports(Enum):
    """Define supported indicators."""

    WATERPROOFING_DATA_FLOODING = 1

    @property
    def constructor(self):
        from ohsome_quality_tool.reports.waterproofing_data_flooding.report import (
            Report as waterproofingDataFloodingReport,
        )

        reports = {1: waterproofingDataFloodingReport}

        return reports[self.value]


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
