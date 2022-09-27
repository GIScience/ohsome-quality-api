from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class SketchmapFitness(BaseReport):
    def set_indicator_layer(self):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("MappingSaturation", "major_roads_length"),
                IndicatorLayer("Currentness", "major_roads_count"),
                IndicatorLayer("Currentness", "amenities"),
                IndicatorLayer("PoiDensity", "poi"),
            ),
            feature=self.feature,
            blocking_red=self.blocking_red,
            blocking_undefined=self.blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
