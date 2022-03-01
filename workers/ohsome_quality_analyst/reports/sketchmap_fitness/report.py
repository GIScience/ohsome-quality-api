from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class SketchmapFitness(BaseReport):
    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "major_roads_length"),
            IndicatorLayer("Currentness", "major_roads_count"),
            IndicatorLayer("Currentness", "amenities"),
            IndicatorLayer("PoiDensity", "poi"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
