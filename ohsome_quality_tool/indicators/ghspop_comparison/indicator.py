import json
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "GHSPOP_COMPARISON"

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = LEVEL_ONE_LAYERS,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
            layers=layers,
        )

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        if self.dynamic:
            pop_count, area = geodatabase.get_zonal_stats_population(bpolys=self.bpolys)
        else:
            pop_count = geodatabase.get_value_from_db(
                dataset=self.dataset,
                feature_id=self.feature_id,
                field_name="population",
            )

        # ideally we would have this as a dataframe?
        preprocessing_results = {
            "pop_count": pop_count,
            "area_sqkm": area,
            "pop_count_per_sqkm": pop_count / area,
        }

        query_results = ohsome_api.process_ohsome_api(
            endpoint="elements/{unit}/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )

        for layer in self.layers.keys():
            unit = self.layers[layer]["unit"]
            preprocessing_results[f"{layer}_{unit}"] = query_results[layer]["result"][
                0
            ]["value"]
            preprocessing_results[f"{layer}_{unit}_per_pop"] = (
                preprocessing_results[f"{layer}_{unit}"] / pop_count
            )

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict):

        results = {
            "data": preprocessing_results,
            "quality_level": "tbd",
            "description": "tbd",
        }

        logger.info(f"run calculation for {self.name} indicator")
        # TODO: classification based on pop and building count

        return results

    def export_figures(self, results: Dict):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
