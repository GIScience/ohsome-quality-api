from typing import Optional, Union

from geojson import MultiPolygon, Polygon

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class SimpleReport(BaseReport):
    def __init__(
        self,
        bpolys: Union[Polygon, MultiPolygon] = None,
        dataset: Optional[str] = None,
        feature_id: Optional[int] = None,
        fid_field: Optional[str] = None,
    ) -> None:
        super().__init__(
            bpolys=bpolys, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "building_count"),
            IndicatorLayer("GhsPopComparisonBuildings", "building_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
