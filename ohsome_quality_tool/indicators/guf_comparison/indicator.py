import json
from typing import Dict, Tuple

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "GUF_COMPARISON"
    description = (
        "Compare OSM features against built up area defined by "
        "Global Urban Footprint dataset."
    )

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = LEVEL_ONE_LAYERS,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: str = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layers=layers,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        if self.dynamic:
            built_up_area, area = geodatabase.get_zonal_stats_guf(bpolys=self.bpolys)
        else:
            built_up_area = geodatabase.get_value_from_db(
                dataset=self.dataset,
                feature_id=self.feature_id,
                field_name="population",
            )

        # ideally we would have this as a dataframe?
        preprocessing_results = {
            "guf_built_up_area_sqkm": built_up_area,
            "area_sqkm": area,
            "guf_built_up_density": built_up_area / area,
        }
        self.layers= {"buildings": {"filter": "buildings=*",
        "unit": "area"}
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
            preprocessing_results[f"{layer}_{unit}_per_guf_built_up"] = (
                preprocessing_results[f"{layer}_{unit}"] / built_up_area
            )

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:

        # TODO: classification based on pop and building count

        # which thresholds?
        
        ratio = preprocessing_results["buildings_area"]/preprocessing_results["guf_built_up_area_sqkm"]
        GreenThreshold = 0.6
        YellowThreshold = 0.2
        
        if ratio <= YellowThreshold:
            value = TrafficLightQualityLevels.RED.value
        elif ratio <= GreenThreshold:
            value = TrafficLightQualityLevels.YELLOW.value
        else: 
            value = TrafficLightQualityLevels.GREEN.value
        
        label = TrafficLightQualityLevels(ceil(value))
        text = "test test test"

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
