from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class MapActionPoc(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("mapping-saturation", "mapaction_settlements_count"),
                IndicatorLayer("mapping-saturation", "mapaction_major_roads_length"),
                IndicatorLayer("mapping-saturation", "mapaction_rail_length"),
                IndicatorLayer("mapping-saturation", "mapaction_lakes_area"),
                IndicatorLayer("mapping-saturation", "mapaction_rivers_length"),
                IndicatorLayer("currentness", "mapaction_settlements_count"),
                IndicatorLayer("currentness", "mapaction_major_roads_length"),
                IndicatorLayer("currentness", "mapaction_rail_length"),
                IndicatorLayer("currentness", "mapaction_lakes_count"),
                IndicatorLayer("currentness", "mapaction_rivers_length"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
