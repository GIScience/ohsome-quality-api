import collections
from enum import Enum
from typing import Dict

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


IndicatorResult = collections.namedtuple("Result", "label value text svg")
IndicatorMetadata = collections.namedtuple("Metadata", "name description")

ReportResult = collections.namedtuple("Result", "label value text")
ReportMetadata = collections.namedtuple("Metadata", "name description")


class TrafficLightQualityLevels(Enum):
    """The Quality Levels"""

    GREEN = 1
    YELLOW = 2
    RED = 3


def get_indicators() -> Dict:
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


# TODO: Is there a better way to define this?
class Reports(Enum):
    """Define supported indicators."""

    SKETCHMAP_FITNESS = 1
    REMOTE_MAPPING_LEVEL_ONE = 2

    @property
    def constructor(self):
        from ohsome_quality_tool.reports.remote_mapping_level_one.report import (
            Report as remoteMappingLevelOneReport,
        )
        from ohsome_quality_tool.reports.sketchmap_fitness.report import (
            Report as sketchmapFitnessReport,
        )

        reports = {1: sketchmapFitnessReport, 2: remoteMappingLevelOneReport}

        return reports[self.value]
