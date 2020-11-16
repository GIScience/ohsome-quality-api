import json

from geojson import FeatureCollection
from ohsome import OhsomeClient

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """The Building Completeness Indicator."""

    name = "building_completeness"

    def __init__(
        self,
        dynamic: bool,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        ohsome_api: str = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic, bpolys=bpolys, dataset=dataset, feature_id=feature_id
        )

        self.osm_building_area: float = 0.0
        self.pop_density: float = 0.0

    def preprocess(self):
        logger.info(f"run preprocessing for {self.name} indicator")

        client = OhsomeClient()
        response = client.elements.area.post(
            bpolys=json.dumps(self.bpolys), filter="building=*"
        )
        self.osm_building_area = response.as_dataframe().iloc[0]["value"]
        logger.info(f"osm building area: {self.osm_building_area}")
        logger.info(f"extracted osm features for {self.name} indicator")

        # TODO: obtain Global Urban Footprint data
        # self.pop_density =

    def calculate(self):
        logger.info(f"run calculation for {self.name} indicator")
        self.results["score"] = 0.5

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
