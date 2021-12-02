from typing import Optional

from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class JrcRequirements(BaseReport):
    def __init__(
        self,
        feature: Feature = None,
        dataset: Optional[str] = None,
        feature_id: Optional[int] = None,
        fid_field: Optional[str] = None,
    ) -> None:
        """Create a list of indicator objects."""

        super().__init__(
            feature=feature, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self) -> None:
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "jrc_health_count"),
            IndicatorLayer("MappingSaturation", "jrc_mass_gathering_sites_count"),
            IndicatorLayer("MappingSaturation", "jrc_railway_length"),
            IndicatorLayer("MappingSaturation", "jrc_road_length"),
            IndicatorLayer("MappingSaturation", "jrc_education_count"),
            IndicatorLayer("Currentness", "jrc_health_count"),
            IndicatorLayer("Currentness", "jrc_education_count"),
            IndicatorLayer("Currentness", "jrc_road_count"),
            IndicatorLayer("Currentness", "jrc_railway_count"),
            IndicatorLayer("Currentness", "jrc_airport_count"),
            IndicatorLayer("Currentness", "jrc_water_treatment_plant_count"),
            IndicatorLayer("Currentness", "jrc_power_generation_plant_count"),
            IndicatorLayer("Currentness", "jrc_cultural_heritage_site_count"),
            IndicatorLayer("Currentness", "jrc_bridge_count"),
            IndicatorLayer("Currentness", "jrc_mass_gathering_sites_count"),
            # TODO define threshoulds for GhsPopComparison with jrc
            #  layer topics
            # IndicatorLayer("GhsPopComparison", "jrc_road_length"),
            # IndicatorLayer("GhsPopComparison", "jrc_railway_length"),
            IndicatorLayer("TagsRatio", "jrc_health_count"),
            IndicatorLayer("TagsRatio", "jrc_education_count"),
            IndicatorLayer("TagsRatio", "jrc_road_length"),
            IndicatorLayer("TagsRatio", "jrc_airport_count"),
            IndicatorLayer("TagsRatio", "jrc_power_generation_plant_count"),
            IndicatorLayer("TagsRatio", "jrc_cultural_heritage_site_count"),
            IndicatorLayer("TagsRatio", "jrc_bridge_count"),
            IndicatorLayer("TagsRatio", "jrc_mass_gathering_sites_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
