from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.definitions import get_attribution


class MultilevelMappingSaturation(BaseReport):
    def set_indicator_layer(self):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("MappingSaturation", "infrastructure_lines"),
                IndicatorLayer("MappingSaturation", "poi"),
                IndicatorLayer("MappingSaturation", "lulc"),
                IndicatorLayer("MappingSaturation", "building_count"),
            ),
            feature=self.feature,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM"])
