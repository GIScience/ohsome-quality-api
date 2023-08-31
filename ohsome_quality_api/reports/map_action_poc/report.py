from geojson import Feature

from ohsome_quality_api.reports.base import BaseReport, IndicatorTopic


class MapActionPoc(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_topic=(
                IndicatorTopic("mapping-saturation", "mapaction-settlements-count"),
                IndicatorTopic("mapping-saturation", "mapaction-major-roads-length"),
                IndicatorTopic("mapping-saturation", "mapaction-rail-length"),
                IndicatorTopic("mapping-saturation", "mapaction-lakes-area"),
                IndicatorTopic("mapping-saturation", "mapaction-rivers-length"),
                IndicatorTopic("currentness", "mapaction-settlements-count"),
                IndicatorTopic("currentness", "mapaction-major-roads-length"),
                IndicatorTopic("currentness", "mapaction-rail-length"),
                IndicatorTopic("currentness", "mapaction-lakes-count"),
                IndicatorTopic("currentness", "mapaction-rivers-length"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
