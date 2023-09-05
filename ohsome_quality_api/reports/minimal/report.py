from ohsome_quality_api.api.request_models import Feature
from ohsome_quality_api.definitions import get_attribution
from ohsome_quality_api.reports.base import BaseReport, IndicatorTopic


class Minimal(BaseReport):
    def __init__(
        self,
        feature: Feature,
        blocking_red: bool = None,
        blocking_undefined: bool = None,
    ):
        super().__init__(
            indicator_topic=(
                IndicatorTopic("mapping-saturation", "building-count"),
                IndicatorTopic("currentness", "building-count"),
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
