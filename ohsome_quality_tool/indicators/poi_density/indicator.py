from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """The POI Density Indicator."""

    name = "POI Density"

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

    def preprocess(self):
        logger.info(f"run preprocessing for {self.name} indicator")

    def calculate(self):
        logger.info(f"run calculation for {self.name} indicator")

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
