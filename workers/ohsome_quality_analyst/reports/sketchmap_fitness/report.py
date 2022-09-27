from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class SketchmapFitness(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("MappingSaturation", "major_roads_length"),
                IndicatorLayer("Currentness", "major_roads_count"),
                IndicatorLayer("Currentness", "amenities"),
                IndicatorLayer("PoiDensity", "poi"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
