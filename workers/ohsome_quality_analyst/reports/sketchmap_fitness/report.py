from typing import Optional, Union

from geojson import MultiPolygon, Polygon

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class SketchmapFitness(BaseReport):
    def __init__(
        self,
        bpolys: Union[Polygon, MultiPolygon, None] = None,
        dataset: Optional[str] = None,
        feature_id: Optional[int] = None,
        fid_field: Optional[str] = None,
    ) -> None:
        super().__init__(
            bpolys=bpolys, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self):
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "major_roads_length"),
            IndicatorLayer("LastEdit", "major_roads_count"),
            IndicatorLayer("LastEdit", "amenities"),
            IndicatorLayer("PoiDensity", "poi"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
