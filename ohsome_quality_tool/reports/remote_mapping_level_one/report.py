from statistics import mean

from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.helper import name_to_class


class RemoteMappingLevelOne(BaseReport):
    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        """Create a list of indicator objects."""

        super().__init__(bpolys=bpolys, dataset=dataset, feature_id=feature_id)
        for indicator_name, layer_name in (
            # TODO ("GufComparison"], "building-area"),
            # ("MappingSaturation", "building_count"),
            # ("MappingSaturation", "major_roads"),
            ("GhsPopComparison", "building_count"),
            ("LastEdit", "building_count"),
            ("LastEdit", "major_roads"),
        ):
            indicator_class = name_to_class(class_type="indicator", name=indicator_name)
            indicator = indicator_class(layer_name=layer_name, bpolys=bpolys)
            self.indicators.append(indicator)

    def combine(self):
        """Combine the results of all indicators."""
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
