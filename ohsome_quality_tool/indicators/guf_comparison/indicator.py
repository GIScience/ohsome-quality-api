import json
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "GUF_COMPARISON"

    def __init__(
        self,
        dynamic: bool,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: str = None,
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

        # get area in square kilometers
        feature_area = query_results["buildings"]["result"][0]["value"] / (1000 * 1000)

        if self.dynamic:
            built_up_area = geodatabase.get_zonal_stats_guf(bpolys=self.bpolys)
        else:
            built_up_area = geodatabase.get_value_from_db(
                dataset=self.dataset,
                feature_id=self.feature_id,
                field_name="population",
            )

        # ideally we would have this as a dataframe?
        preprocessing_results = {
            "osm_building_area": feature_area,
            "guf_built_up_area": built_up_area,
        }

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict):

        results = {}

        logger.info(f"run calculation for {self.name} indicator")
        results["feature_area_per_built_up_area"] = (
            preprocessing_results["osm_building_area"]
            / preprocessing_results["guf_built_up_area"]
        )

        # TODO: classification based on pop and building count

        return results

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
