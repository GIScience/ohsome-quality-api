from ohsome_quality_analyst.reports.base import BaseReport, IndicatorTopic
from ohsome_quality_analyst.utils.definitions import get_attribution


class RemoteMappingLevelOne(BaseReport):
    def set_indicator_layer(self) -> None:
        super().__init__(
            indicator_topic=(
                # TODO: Uncomment once implemented
                # IndicatorTopic("GufComparison"], "building-area"),
                IndicatorTopic("MappingSaturation", "building-count"),
                IndicatorTopic("MappingSaturation", "major-roads-length"),
                IndicatorTopic("Currentness", "building-count"),
                IndicatorTopic("Currentness", "major-roads-count"),
            )
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])
