from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.definitions import Indicators
from ohsome_quality_tool.utils.layers import (
    SKETCHMAP_FITNESS_FEATURES,
    SKETCHMAP_FITNESS_POI_LAYER,
)


class Report(BaseReport):
    """The Sketchmap Fitness Report."""

    name = "SKETCHMAP_FITNESS"
    indicators = [
        (Indicators.MAPPING_SATURATION, SKETCHMAP_FITNESS_FEATURES),
        (Indicators.POI_DENSITY, SKETCHMAP_FITNESS_POI_LAYER),
        (Indicators.LAST_EDIT, SKETCHMAP_FITNESS_FEATURES),
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

    def combine_indicators(self):
        """Combine the individual scores per indicator."""
        logger.info(f"combine indicators for {self.name} report.")

        self.results["quality_level"] = "tbd"
        self.results["description"] = "tbd"
