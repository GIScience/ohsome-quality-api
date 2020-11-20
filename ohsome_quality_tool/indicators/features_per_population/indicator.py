import json
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "FEATURES_PER_POPULATION"

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
            endpoint="/elements/count/",
            categories=categories,
            bpolys=json.dumps(self.bpolys),
        )

        feature_count = query_results["buildings"]["result"][0]["value"]

        if self.dynamic:
            pop_count = geodatabase.get_zonal_stats_population(bpolys=self.bpolys)
        else:
            pop_count = geodatabase.get_value_from_db(
                dataset=self.dataset,
                feature_id=self.feature_id,
                field_name="population",
            )

        # ideally we would have this as a dataframe?
        preprocessing_results = {
            "osm_building_area": feature_count,
            "pop_count": pop_count,
        }

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict):

        results = {}

        logger.info(f"run calculation for {self.name} indicator")
        results["features_per_pop"] = (
            preprocessing_results["osm_building_area"]
            / preprocessing_results["pop_count"]
        )

        # TODO: classification based on pop and building count

        return results

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
