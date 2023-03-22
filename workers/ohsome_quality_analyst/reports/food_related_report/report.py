from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.definitions import get_attribution


class FoodRelatedReport(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = True,
        blocking_undefined: bool = True,
    ):
        super().__init__(
            indicator_layer=(
                IndicatorLayer("mapping-saturation", "local_food_shops"),
                IndicatorLayer("currentness", "local_food_shops"),
                IndicatorLayer("mapping-saturation", "fast_food_restaurants"),
                IndicatorLayer("currentness", "fast_food_restaurants"),
                IndicatorLayer("Mapping-saturation", "restaurants"),
                IndicatorLayer("currentness", "restaurants"),
                IndicatorLayer("mapping-saturation", "supermarkets"),
                IndicatorLayer("currentness", "supermarkets"),
                IndicatorLayer("mapping-saturation", "convenience_stores"),
                IndicatorLayer("currentness", "convenience_stores"),
                IndicatorLayer("mapping-saturation", "pubs_and_biergartens"),
                IndicatorLayer("currentness", "pubs_and_biergartens"),
                IndicatorLayer("mapping-saturation", "alcohol_and_beverages"),
                IndicatorLayer("currentness", "alcohol_and_beverages"),
                IndicatorLayer("mapping-saturation", "sweets_and_pasteries"),
                IndicatorLayer("currentness", "sweets_and_pasteries"),
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
