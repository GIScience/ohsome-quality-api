from geojson import FeatureCollection

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class MapActionPoc(BaseReport):
    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        fid_field: str = None,
    ) -> None:
        """Create a list of indicator objects."""

        super().__init__(
            bpolys=bpolys, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self) -> None:
        self.indicator_layer = (
            IndicatorLayer("MappingSaturation", "mapaction_settlements_count"),
            IndicatorLayer("MappingSaturation", "mapaction_capital_city_count"),
            IndicatorLayer("MappingSaturation", "major_roads_length"),
            IndicatorLayer("LastEdit", "mapaction_settlements_count"),
            IndicatorLayer("LastEdit", "mapaction_capital_city_count"),
            IndicatorLayer("LastEdit", "major_roads_length"),
            IndicatorLayer("LastEdit", "mapaction_lakes_count"),
            IndicatorLayer("LastEdit", "mapaction_rivers_length"),
            IndicatorLayer("LastEdit", "mapaction_rail_length"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
