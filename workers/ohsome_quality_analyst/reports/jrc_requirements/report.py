from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class JrcRequirements(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("mapping-saturation", "jrc_health_count"),
                IndicatorLayer("mapping-saturation", "jrc_mass_gathering_sites_count"),
                IndicatorLayer("mapping-saturation", "jrc_railway_length"),
                IndicatorLayer("mapping-saturation", "jrc_road_length"),
                IndicatorLayer("mapping-saturation", "jrc_education_count"),
                IndicatorLayer("currentness", "jrc_health_count"),
                IndicatorLayer("currentness", "jrc_education_count"),
                IndicatorLayer("currentness", "jrc_road_count"),
                IndicatorLayer("currentness", "jrc_railway_count"),
                IndicatorLayer("currentness", "jrc_airport_count"),
                IndicatorLayer("currentness", "jrc_water_treatment_plant_count"),
                IndicatorLayer("currentness", "jrc_power_generation_plant_count"),
                IndicatorLayer("currentness", "jrc_cultural_heritage_site_count"),
                IndicatorLayer("currentness", "jrc_bridge_count"),
                IndicatorLayer("currentness", "jrc_mass_gathering_sites_count"),
                # TODO define thresholds for GhsPopComparison with jrc
                #  layer topics
                # IndicatorLayer("GhsPopComparison", "jrc_road_length"),
                # IndicatorLayer("GhsPopComparison", "jrc_railway_length"),
                IndicatorLayer("tags-ratio", "jrc_health_count"),
                IndicatorLayer("tags-ratio", "jrc_education_count"),
                IndicatorLayer("tags-ratio", "jrc_road_length"),
                IndicatorLayer("tags-ratio", "jrc_airport_count"),
                IndicatorLayer("tags-ratio", "jrc_power_generation_plant_count"),
                IndicatorLayer("tags-ratio", "jrc_cultural_heritage_site_count"),
                IndicatorLayer("tags-ratio", "jrc_bridge_count"),
                IndicatorLayer("tags-ratio", "jrc_mass_gathering_sites_count"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
