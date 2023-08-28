from geojson import Feature

from ohsome_quality_api.definitions import get_attribution
from ohsome_quality_api.reports.base import BaseReport, IndicatorTopic


class FoodRelatedReport(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = True,
        blocking_undefined: bool = True,
    ):
        super().__init__(
            indicator_topic=(
                IndicatorTopic("mapping-saturation", "local_food_shops"),
                IndicatorTopic("currentness", "local_food_shops"),
                IndicatorTopic("mapping-saturation", "fast_food_restaurants"),
                IndicatorTopic("currentness", "fast_food_restaurants"),
                IndicatorTopic("mapping-saturation", "restaurants"),
                IndicatorTopic("currentness", "restaurants"),
                IndicatorTopic("mapping-saturation", "supermarkets"),
                IndicatorTopic("currentness", "supermarkets"),
                IndicatorTopic("mapping-saturation", "convenience_stores"),
                IndicatorTopic("currentness", "convenience_stores"),
                IndicatorTopic("mapping-saturation", "pubs_and_biergartens"),
                IndicatorTopic("currentness", "pubs_and_biergartens"),
                IndicatorTopic("mapping-saturation", "alcohol_and_beverages"),
                IndicatorTopic("currentness", "alcohol_and_beverages"),
                IndicatorTopic("mapping-saturation", "sweets_and_pasteries"),
                IndicatorTopic("currentness", "sweets_and_pasteries"),
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
