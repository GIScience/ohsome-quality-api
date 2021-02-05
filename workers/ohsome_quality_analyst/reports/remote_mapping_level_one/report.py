from statistics import mean

from geojson import FeatureCollection

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.utils.definitions import TrafficLightQualityLevels, logger


class RemoteMappingLevelOne(BaseReport):
    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        """Create a list of indicator objects."""

        super().__init__(bpolys=bpolys, dataset=dataset, feature_id=feature_id)

    def set_indicator_layer(self) -> None:
        self.indicator_layer = (
            # TODO: Uncomment once implemented
            # IndicatorLayer("GufComparison"], "building_area"),
            IndicatorLayer("MappingSaturation", "building_count"),
            IndicatorLayer("MappingSaturation", "major_roads"),
            IndicatorLayer("GhsPopComparison", "building_count"),
            IndicatorLayer("LastEdit", "building_count"),
            IndicatorLayer("LastEdit", "major_roads"),
        )

    def combine_indicators(self) -> None:
        logger.info(f"Combine indicators for report: {self.metadata.name}")

        values = []
        for indicator in self.indicators:
            # TODO: Is it possible that a label == UNDEFINED?
            if indicator.result.label != "UNDEFINED":
                values.append(indicator.result.value)
        self.result.value = mean(values)

        if self.result.value < 0.5:
            self.result.label = TrafficLightQualityLevels.RED
            self.result.description = self.metadata.label_description["red"]
        elif self.result.value < 1:
            self.result.label = TrafficLightQualityLevels.YELLOW
            self.result.description = self.metadata.label_description["yellow"]
        elif self.result.value >= 1:
            self.result.label = TrafficLightQualityLevels.GREEN
            self.result.description = self.metadata.label_description["green"]
        else:
            self.result.label = None
            self.result.description = "Could not derive quality level"
