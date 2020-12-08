import collections
import logging.config
import os
from enum import Enum
from pathlib import Path
from typing import Dict

from xdg import XDG_DATA_HOME

DATASET_NAMES = (
    "nuts_rg_60m_2021",
    "nuts_rg_01m_2021",
    "isea3h_world_res_6_hex",
    "isea3h_world_res_12_hex",
    "gadm",
    "gadm_level_0",
    "gadm_level_1",
    "gadm_level_2",
    "gadm_level_3",
    "gadm_level_4",
    "gadm_level_5",
)

OHSOME_API = os.getenv("OHSOME_API", default="https://api.ohsome.org/v1/")

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


IndicatorResult = collections.namedtuple("Result", "label value text svg")
IndicatorMetadata = collections.namedtuple("Metadata", "name description")

ReportResult = collections.namedtuple("Result", "label value text")
ReportMetadata = collections.namedtuple("Metadata", "name description")


class TrafficLightQualityLevels(Enum):
    """The Quality Levels"""

    GREEN = 1
    YELLOW = 2
    RED = 3


def get_indicator_classes() -> Dict:
    """Map indicator name to corresponding class"""
    # To avoid circular imports classes are imported only once this function is called.
    from ohsome_quality_tool.indicators.ghspop_comparison.indicator import (
        Indicator as ghspopComparisonIndicator,
    )
    from ohsome_quality_tool.indicators.guf_comparison.indicator import (
        Indicator as gufComparisonIndicator,
    )
    from ohsome_quality_tool.indicators.last_edit.indicator import (
        Indicator as lastEditIndicator,
    )
    from ohsome_quality_tool.indicators.mapping_saturation.indicator import (
        Indicator as mappingSaturationIndicator,
    )
    from ohsome_quality_tool.indicators.poi_density.indicator import (
        Indicator as poiDensityIndicator,
    )

    return {
        "GHSPOP_COMPARISON": ghspopComparisonIndicator,
        "POI_DENSITY": poiDensityIndicator,
        "LAST_EDIT": lastEditIndicator,
        "MAPPING_SATURATION": mappingSaturationIndicator,
        "GUF_COMPARISON": gufComparisonIndicator,
    }


def get_report_classes() -> Dict:
    """Map report name to corresponding class."""
    # To avoid circular imports classes are imported only once this function is called.
    from ohsome_quality_tool.reports.remote_mapping_level_one.report import (
        Report as remoteMappingLevelOneReport,
    )
    from ohsome_quality_tool.reports.simple_report.report import Report as simpleReport
    from ohsome_quality_tool.reports.sketchmap_fitness.report import (
        Report as sketchmapFitnessReport,
    )

    return {
        "SKETCHMAP_FITNESS": sketchmapFitnessReport,
        "REMOTE_MAPPING_LEVEL_ONE": remoteMappingLevelOneReport,
        "SIMPLE_REPORT": simpleReport,
    }
