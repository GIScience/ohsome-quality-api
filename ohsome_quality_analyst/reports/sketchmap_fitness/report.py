from geojson import Feature

from ohsome_quality_analyst.reports.base import BaseReport, IndicatorTopic


class SketchmapFitness(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_topic=(
                IndicatorTopic("mapping-saturation", "major-roads-length"),
                IndicatorTopic("currentness", "major-roads-length"),
                IndicatorTopic("currentness", "amenities"),
                IndicatorTopic("density", "landmarks"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
