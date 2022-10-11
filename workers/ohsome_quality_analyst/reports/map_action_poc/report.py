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
                IndicatorLayer("MappingSaturation", "mapaction_settlements_count"),
                IndicatorLayer("MappingSaturation", "mapaction_major_roads_length"),
                IndicatorLayer("MappingSaturation", "mapaction_rail_length"),
                IndicatorLayer("MappingSaturation", "mapaction_lakes_area"),
                IndicatorLayer("MappingSaturation", "mapaction_rivers_length"),
                IndicatorLayer("Currentness", "mapaction_settlements_count"),
                IndicatorLayer("Currentness", "mapaction_major_roads_length"),
                IndicatorLayer("Currentness", "mapaction_rail_length"),
                IndicatorLayer("Currentness", "mapaction_lakes_count"),
                IndicatorLayer("Currentness", "mapaction_rivers_length"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
