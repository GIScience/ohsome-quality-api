from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.utils.definitions import get_attribution


class RemoteMappingLevelOne(BaseReport):
    def set_indicator_layer(self) -> None:
        self.indicator_layer = (
            # TODO: Uncomment once implemented
            # IndicatorLayer("GufComparison"], "building_area"),
            IndicatorLayer("MappingSaturation", "building_count"),
            IndicatorLayer("MappingSaturation", "major_roads_length"),
            IndicatorLayer("GhsPopComparisonRoads", "major_roads_length"),
            IndicatorLayer("GhsPopComparisonBuildings", "building_count"),
            IndicatorLayer("Currentness", "building_count"),
            IndicatorLayer("Currentness", "major_roads_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])
