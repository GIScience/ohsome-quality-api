from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.definitions import get_attribution


class Minimal(BaseReport):
    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "building_count"),
            IndicatorLayer("Currentness", "building_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM"])
