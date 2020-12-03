import json
from typing import Dict, Tuple

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels
from ohsome_quality_tool.utils.layers import SKETCHMAP_FITNESS_POI_LAYER_COMBINED

# threshold values defining the color of the traffic light derived directly from sketchmap_fitness repo
THRESHOLD_YELLOW = 30
THRESHOLD_RED = 10

class Indicator(BaseIndicator):
    """The POI Density Indicator."""

    name = "POI_DENSITY"
    description = """
        Derive the density of OSM features
    """

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = SKETCHMAP_FITNESS_POI_LAYER_COMBINED,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
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

        query_results = ohsome_api.process_ohsome_api(
            endpoint="elements/count/density/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )

        preprocessing_results = {}

        for layer in self.layers.keys():
            preprocessing_results[f"{layer}_density"] = query_results[layer]["result"][0]["value"]

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")

        result = preprocessing_results["combined_density"]
        
        # we still need to think of how to better define the values and text here
        if result > THRESHOLD_YELLOW:
            label = TrafficLightQualityLevels.GREEN
            value = 0.75
            text = "super green!"
        elif THRESHOLD_YELLOW >= result > THRESHOLD_RED:
            label = TrafficLightQualityLevels.YELLOW
            value = 0.5
            text = "medium yellow."
        else:
            label = TrafficLightQualityLevels.RED
            value = 0.25
            text = "bad red"
            
        logger.info(f"result density value: " + str(result) + " label: " + str(label) + " value: " + str(value) + " text: " + text)

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
