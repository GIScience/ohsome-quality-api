import logging
from statistics import mean

from geojson import FeatureCollection

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class JrcRequirements(BaseReport):
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
            IndicatorLayer("MappingSaturation", "jrc_health_count"),
            IndicatorLayer("MappingSaturation", "jrc_mass_gathering_sites_count"),
            IndicatorLayer("MappingSaturation", "jrc_railway_length"),
            IndicatorLayer("MappingSaturation", "jrc_road_length"),
            # IndicatorLayer("LastEdit", "jrc_health_count"),
            # IndicatorLayer("LastEdit", "jrc_education_count"),
            # IndicatorLayer("LastEdit", "jrc_road_length"),
            # IndicatorLayer("LastEdit", "jrc_railway_length"),
            # IndicatorLayer("LastEdit", "jrc_airport_count"),
            # IndicatorLayer("LastEdit", "jrc_water_treatment_plant_count"),
            # IndicatorLayer("LastEdit", "jrc_power_generation_plant_count"),
            # IndicatorLayer("LastEdit", "jrc_cultural_heritage_site_count"),
            # IndicatorLayer("LastEdit", "jrc_bridge_count"),
            # IndicatorLayer("LastEdit", "jrc_mass_gathering_sites_count"),
        )

    def combine_indicators(self) -> None:
        logging.info(f"Combine indicators for report: {self.metadata.name}")

        values = []
        for indicator in self.indicators:
            # TODO: Is it possible that a label == UNDEFINED?
            if indicator.result.label != "UNDEFINED":
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
