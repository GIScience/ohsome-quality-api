from typing import Optional

from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer


class RemoteMappingLevelOne(BaseReport):
    def __init__(
        self,
        feature: Feature = None,
        dataset: Optional[str] = None,
        feature_id: Optional[int] = None,
        fid_field: Optional[str] = None,
    ) -> None:
        """Create a list of indicator objects."""

        super().__init__(
            feature=feature, dataset=dataset, feature_id=feature_id, fid_field=fid_field
        )

    def set_indicator_layer(self) -> None:
        self.indicator_layer = (
            # TODO: Uncomment once implemented
            # IndicatorLayer("GufComparison"], "building_area"),
            IndicatorLayer("MappingSaturation", "building_count"),
            IndicatorLayer("MappingSaturation", "major_roads_length"),
            IndicatorLayer("GhsPopComparisonRoads", "major_roads_length"),
            IndicatorLayer("GhsPopComparisonBuildings", "building_count"),
            IndicatorLayer("LastEdit", "building_count"),
            IndicatorLayer("LastEdit", "major_roads_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()
