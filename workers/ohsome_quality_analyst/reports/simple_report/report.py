from geojson import FeatureCollection

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class SimpleReport(BaseReport):
    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        fid_field: str = None,
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
