from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.utils.definitions import get_attribution


class MultilevelMappingSaturation(BaseReport):
    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "ideal_vgi_infrastructur"),
            IndicatorLayer("MappingSaturation", "poi"),
            IndicatorLayer("MappingSaturation", "lulc"),
            IndicatorLayer("MappingSaturation", "building_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM"])
