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
                # TODO define thresholds for GhsPopComparison with jrc
                #  layer topics
                # IndicatorLayer("GhsPopComparison", "jrc_road_length"),
                # IndicatorLayer("GhsPopComparison", "jrc_railway_length"),
                IndicatorLayer("AttributeCompleteness", "jrc_health_count"),
                IndicatorLayer("AttributeCompleteness", "jrc_education_count"),
                IndicatorLayer("AttributeCompleteness", "jrc_road_length"),
                IndicatorLayer("AttributeCompleteness", "jrc_airport_count"),
                IndicatorLayer(
                    "AttributeCompleteness", "jrc_power_generation_plant_count"
                ),
                IndicatorLayer(
                    "AttributeCompleteness", "jrc_cultural_heritage_site_count"
                ),
                IndicatorLayer("AttributeCompleteness", "jrc_bridge_count"),
                IndicatorLayer(
                    "AttributeCompleteness", "jrc_mass_gathering_sites_count"
                ),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
