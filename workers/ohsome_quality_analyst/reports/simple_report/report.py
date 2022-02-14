from typing import Optional

from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.utils.definitions import get_attribution


class SimpleReport(BaseReport):
    def __init__(
        self,
        feature: Feature = None,
        dataset: Optional[str] = None,
        feature_id: Optional[int] = None,
        fid_field: Optional[str] = None,
    ) -> None:
        super().__init__(
            feature=feature, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "building_count"),
            IndicatorLayer("GhsPopComparisonBuildings", "building_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])
