from typing import Optional, Union

from geojson import MultiPolygon, Polygon

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class MapActionPoc(BaseReport):
    def __init__(
        self,
        bpolys: Union[Polygon, MultiPolygon, None] = None,
        dataset: Optional[str] = None,
        feature_id: Optional[int] = None,
        fid_field: Optional[str] = None,
    ) -> None:
        """Create a list of indicator objects."""

        super().__init__(
            bpolys=bpolys, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self) -> None:
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "mapaction_settlements_count"),
            IndicatorLayer("MappingSaturation", "mapaction_major_roads_length"),
            IndicatorLayer("MappingSaturation", "mapaction_rail_length"),
            IndicatorLayer("MappingSaturation", "mapaction_lakes_area"),
            IndicatorLayer("MappingSaturation", "mapaction_rivers_length"),
            IndicatorLayer("LastEdit", "mapaction_settlements_count"),
            IndicatorLayer("LastEdit", "mapaction_major_roads_length"),
            IndicatorLayer("LastEdit", "mapaction_rail_length"),
            IndicatorLayer("LastEdit", "mapaction_lakes_count"),
            IndicatorLayer("LastEdit", "mapaction_rivers_length"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
