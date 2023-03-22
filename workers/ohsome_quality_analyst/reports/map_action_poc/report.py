from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorTopic


class MapActionPoc(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_topic=(
                IndicatorTopic("mapping-saturation", "mapaction_settlements_count"),
                IndicatorTopic("mapping-saturation", "mapaction_major_roads_length"),
                IndicatorTopic("mapping-saturation", "mapaction_rail_length"),
                IndicatorTopic("mapping-saturation", "mapaction_lakes_area"),
                IndicatorTopic("mapping-saturation", "mapaction_rivers_length"),
                IndicatorTopic("currentness", "mapaction_settlements_count"),
                IndicatorTopic("currentness", "mapaction_major_roads_length"),
                IndicatorTopic("currentness", "mapaction_rail_length"),
                IndicatorTopic("currentness", "mapaction_lakes_count"),
                IndicatorTopic("currentness", "mapaction_rivers_length"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
