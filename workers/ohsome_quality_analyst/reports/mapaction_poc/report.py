import logging
from statistics import mean

from geojson import FeatureCollection

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class MapActionPOC(BaseReport):
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
            IndicatorLayer("MappingSaturation", "mapaction_settlements_count"),
            IndicatorLayer("MappingSaturation", "mapaction_capital_city_count"),
            IndicatorLayer("MappingSaturation", "major_roads"),
            IndicatorLayer("LastEdit", "mapaction_settlements_count"),
            IndicatorLayer("LastEdit", "mapaction_capital_city_count"),
            IndicatorLayer("LastEdit", "major_roads"),
            IndicatorLayer("LastEdit", "mapaction_lakes_count"),
            IndicatorLayer("LastEdit", "mapaction_rivers_length"),
            IndicatorLayer("LastEdit", "major_rail_length"),
        )

    def combine_indicators(self) -> None:
        logging.info(f"Combine indicators for report: {self.metadata.name}")

        values = []
        for indicator in self.indicators:
            if indicator.result.label != "undefined":
                values.append(indicator.result.value)
        self.result.value = mean(values)

        if self.result.value < 0.5:
            self.result.label = "red"
            self.result.description = self.metadata.label_description["red"]
        elif self.result.value < 1:
            self.result.label = "yellow"
            self.result.description = self.metadata.label_description["yellow"]
        elif self.result.value >= 1:
            self.result.label = "green"
            self.result.description = self.metadata.label_description["green"]
        else:
            self.result.label = None
            self.result.description = "Could not derive quality level"
