from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class BuildingReport(BaseReport):
    def set_indicator_layer(self):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("MappingSaturation", "building_count"),
                IndicatorLayer("Currentness", "building_count"),
                IndicatorLayer("TagsRatio", "building_count"),
                IndicatorLayer("BuildingCompleteness", "building_area"),
            )
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
