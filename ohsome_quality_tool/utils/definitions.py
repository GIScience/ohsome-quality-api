import logging.config
import os
from enum import Enum, unique
from pathlib import Path

from xdg import XDG_DATA_HOME

# TODO: this should reflect the major categories
#   ideally they will be useful for many indicators
#   specific reports might define a custom set of categories
#   and respective filters
#   ideally this list should be shorter
#   e.g. come up with roads, buildings, amenities, healthcare
#   as the main categories to consider
DEFAULT_CATEGORIES = {
    "mountain": "natural=peak",
    "gas_stations": "amenity=fuel",
    "parks": "leisure=park or boundary=national_park",
    "waterways": "natural=water or waterway=*",
    "health_fac_pharmacies": "amenity in (pharmacy, hospital)",
    "eduction": "amenity in (school, college, university)",
    "public_safety": "amenity in (police, fire_station)",
    "public_transport": "highway=bus_stop or railway=station",
    "hotel": "tourism=hotel",
    "attraction": "tourism=attraction",
    "restaurant": "amenity=restaurant",
    "townhall": "amenity=townhall",
    "shop": "shop=*",
}


# TODO: Is there a better way to define this?
@unique
class Indicators(Enum):
    """Define supported indicators."""

    BUILDING_COMPLETENESS = 1
    POI_DENSITY = 2
    LAST_EDIT = 3
    MAPPING_SATURATION = 4

    @property
    def constructor(self):
        from ohsome_quality_tool.indicators.building_completeness.indicator import (
            Indicator as buildingCompletenessIndicator,
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

        indicators = {
            1: buildingCompletenessIndicator,
            2: poiDensityIndicator,
            3: lastEditIndicator,
            4: mappingSaturationIndicator,
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
