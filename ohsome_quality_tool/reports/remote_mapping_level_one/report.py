from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.definitions import Indicators
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Report(BaseReport):
    """The remote mapping level one Report."""

    name = "REMOTE_MAPPING_LEVEL_ONE"
    description = """
        This report shows the quality for map features that are usually
        added on the basis of satellite imagery.
    """

    indicators_definition = [
        (Indicators.GHSPOP_COMPARISON, LEVEL_ONE_LAYERS),
        (Indicators.GUF_COMPARISON, LEVEL_ONE_LAYERS),
        (Indicators.MAPPING_SATURATION, LEVEL_ONE_LAYERS),
        (Indicators.LAST_EDIT, LEVEL_ONE_LAYERS),
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

        self.result["quality_level"] = "tbd"
        self.result["description"] = "tbd"
