import json
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """The Building Completeness Indicator."""

    name = "BUILDING_COMPLETENESS"

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

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        # category name as key, filter string as value
        categories = {
            "buildings": "building=*",
        }

        query_results = ohsome_api.query_ohsome_api(
            endpoint="/elements/area/",
            categories=categories,
            bpolys=json.dumps(self.bpolys),
        )

        osm_building_area = query_results["buildings"]["result"][0]["value"]

        # TODO: obtain Global Urban Footprint data
        pop_count = 160355

        # ideally we would have this as a dataframe?
        preprocessing_results = {
            "osm_building_area": osm_building_area,
            "pop_count": pop_count,
        }

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict):

        results = {}

        logger.info(f"run calculation for {self.name} indicator")
        results["score"] = (
            preprocessing_results["osm_building_area"]
            / preprocessing_results["pop_count"]
        )

        return results

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
