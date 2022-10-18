from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.definitions import get_attribution


class MultilevelMappingSaturation(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("MappingSaturation", "infrastructure_lines"),
                IndicatorLayer("MappingSaturation", "poi"),
                IndicatorLayer("MappingSaturation", "lulc"),
                IndicatorLayer("MappingSaturation", "building_count"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM"])
