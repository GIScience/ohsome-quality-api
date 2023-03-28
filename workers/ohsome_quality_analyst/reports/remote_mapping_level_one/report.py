from ohsome_quality_analyst.reports.base import BaseReport, IndicatorTopic
from ohsome_quality_analyst.utils.definitions import get_attribution


class RemoteMappingLevelOne(BaseReport):
    def set_indicator_layer(self) -> None:
        super().__init__(
            indicator_topic=(
                # TODO: Uncomment once implemented
                # IndicatorTopic("GufComparison"], "building_area"),
                IndicatorTopic("MappingSaturation", "building_count"),
                IndicatorTopic("MappingSaturation", "major_roads_length"),
                IndicatorTopic("Currentness", "building_count"),
                IndicatorTopic("Currentness", "major_roads_count"),
            )
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])
