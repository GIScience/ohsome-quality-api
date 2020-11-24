from enum import Enum, unique

# TODO: Is there a better way to define this?
DATASETS = [
    "nuts_rg_60m_2021",
    "nuts_rg_01m_2021",
    "isea3h_world_res_6_hex",
    "isea3h_world_res_12_hex",
]


# TODO: Is there a better way to define this?
@unique
class Indicators(Enum):
    """Define supported indicators."""

    GHSPOP_COMPARISON = 1
    POI_DENSITY = 2
    LAST_EDIT = 3
    MAPPING_SATURATION = 4
    GUF_COMPARISON = 5

    @property
    def constructor(self):
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

        indicators = {
            1: ghspopComparisonIndicator,
            2: poiDensityIndicator,
            3: lastEditIndicator,
            4: mappingSaturationIndicator,
            5: gufComparisonIndicator,
        }

        return indicators[self.value]


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
