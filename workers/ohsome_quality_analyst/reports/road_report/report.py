from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.definitions import get_attribution


class RoadReport(BaseReport):
    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "major_roads_length"),
            IndicatorLayer("Currentness", "major_roads_count"),
            IndicatorLayer("TagsRatio", "major_roads_length"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM"])
