from statistics import mean

from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport, IndicatorLayer
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger


class SketchmapFitness(BaseReport):
    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(bpolys=bpolys, dataset=dataset, feature_id=feature_id)

    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "major_roads"),
            IndicatorLayer("LastEdit", "major_roads"),
            IndicatorLayer("LastEdit", "amenities"),
            IndicatorLayer("PoiDensity", "poi"),
        )

    def combine_indicators(self) -> None:
        logger.info(f"Combine indicators for report: {self.metadata.name}")

        # get mean of indicator quality values
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
