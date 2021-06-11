import logging
from statistics import mean

from geojson import FeatureCollection

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class MapActionPoc(BaseReport):
    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        fid_field: str = None,
    ) -> None:
        """Create a list of indicator objects."""

        super().__init__(
            bpolys=bpolys, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self) -> None:
        self.indicator_layer = (           
        	IndicatorLayer("MappingSaturation", "mapaction_settlements_count"),
            IndicatorLayer("MappingSaturation", "mapaction_major_roads_length"),
            IndicatorLayer("MappingSaturation", "mapaction_rail_length"),
            IndicatorLayer("MappingSaturation", "mapaction_lakes_area"),
            IndicatorLayer("MappingSaturation", "mapaction_rivers_length"),
            IndicatorLayer("LastEdit", "mapaction_settlements_count"),
            IndicatorLayer("LastEdit", "mapaction_major_roads_length"),
            IndicatorLayer("LastEdit", "mapaction_rail_length"),
            IndicatorLayer("LastEdit", "mapaction_lakes_count"),
            IndicatorLayer("LastEdit", "mapaction_rivers_length"),
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
