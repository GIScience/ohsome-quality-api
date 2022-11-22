from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.definitions import get_attribution


class FoodRelatedReport(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("MappingSaturation", "local_food_shops"),
                IndicatorLayer("Currentness", "local_food_shops"),
                IndicatorLayer("MappingSaturation", "fast_food_restaurants"),
                IndicatorLayer("Currentness", "fast_food_restaurants"),
                IndicatorLayer("MappingSaturation", "restaurants"),
                IndicatorLayer("Currentness", "restaurants"),
                IndicatorLayer("MappingSaturation", "supermarkets"),
                IndicatorLayer("Currentness", "supermarkets"),
                IndicatorLayer("MappingSaturation", "convenience_stores"),
                IndicatorLayer("Currentness", "convenience_stores"),
                IndicatorLayer("MappingSaturation", "pubs_and_biergartens"),
                IndicatorLayer("Currentness", "pubs_and_biergartens"),
                IndicatorLayer("MappingSaturation", "alcohol_and_beverages"),
                IndicatorLayer("Currentness", "alcohol_and_beverages"),
                IndicatorLayer("MappingSaturation", "sweets_and_pasteries"),
                IndicatorLayer("Currentness", "sweets_and_pasteries"),
            ),
            feature=feature,
            blocking_red=blocking_red,
            blocking_undefined=blocking_undefined,
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM"])
