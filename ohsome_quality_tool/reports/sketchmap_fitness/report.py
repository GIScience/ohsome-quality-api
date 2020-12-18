from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.definitions import (
    ReportResult,
    TrafficLightQualityLevels,
    get_indicator_classes,
    logger,
)
from ohsome_quality_tool.utils.layers import (
    AMENITIES_LAYER,
    MAJOR_ROADS_LAYER,
    POI_LAYER,
)


class Report(BaseReport):
    """The Sketchmap Fitness Report."""

    name = "sketchmap-fitness"
    description = "The sketchmap fitness report."

    indicator_classes: Dict = get_indicator_classes()
    indicators_definition = [
        (indicator_classes["mapping-saturation"], MAJOR_ROADS_LAYER),
        (indicator_classes["last-edit"], MAJOR_ROADS_LAYER),
        (indicator_classes["last-edit"], AMENITIES_LAYER),
        (indicator_classes["poi-density"], POI_LAYER),
    ]

    def __init__(
        self,
        dynamic: bool,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic, bpolys=bpolys, dataset=dataset, feature_id=feature_id
        )

    def combine_indicators(self, indicators) -> ReportResult:
        """Combine the individual scores per indicator."""
        logger.info(f"combine indicators for {self.name} report.")

        result = ReportResult(
            label=TrafficLightQualityLevels.YELLOW, value=0.5, text="test test test"
        )
        return result
