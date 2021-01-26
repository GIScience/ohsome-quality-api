from statistics import mean

from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.definitions import (
    ReportResult,
    TrafficLightQualityLevels,
    logger,
)
from ohsome_quality_tool.utils.helter import name_to_class


class RemoteMappingLevel(BaseReport):
    """The remote mapping level one Report."""

    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(bpolys=bpolys, dataset=dataset, feature_id=feature_id)
        for indicator_name, layer_name in (
            # TODO ("GufComparison"], "building-area"),
            ("GhsPopComparison", "building-count"),
            ("MappingSaturation", "building-count"),
            ("LastEdit", "building-count"),
            ("MappingSaturation", "major-roads"),
            ("LastEdit", "major-roads"),
        ):
            indicator_class = name_to_class(class_type="indicator", name=indicator_name)
            indicator = indicator_class(layer_name=layer_name, bpolys=bpolys)
            self.indicators.append(indicator)

    def combine(self, indicators) -> ReportResult:
        """Combine the individual scores per indicator."""
        logger.info(f"Combine indicators for report: {self.metadata.name}")

        values = []
        for indicator in self.indicators:
            # TODO: When is label == UNDEFINED?
            if indicator.result.label != "UNDEFINED":
                values.append(indicator.result.value)
        self.result.value = mean(values)

        if self.result.value < 0.5:
            self.result.label = TrafficLightQualityLevels.RED
            self.result.description = self.interpretations["red"]
        elif self.result.value < 1:
            self.result.label = TrafficLightQualityLevels.YELLOW
            self.result.description = self.interpretations["yellow"]
        elif self.result.value >= 1:
            self.result.label = TrafficLightQualityLevels.GREEN
            self.result.description = self.interpretations["green"]
        else:
            self.result.label = None
            self.result.description = "Could not derive quality level"
