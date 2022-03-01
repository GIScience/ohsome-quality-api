from typing import Optional

from geojson import Feature

from ohsome_quality_analyst.base.report import BaseReport, IndicatorLayer
from ohsome_quality_analyst.utils.definitions import get_attribution


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
            IndicatorLayer("Currentness", "building_count"),
            IndicatorLayer("Currentness", "major_roads_count"),
        )

    def combine_indicators(self) -> None:
        super().combine_indicators()

    @classmethod
    @property
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])
