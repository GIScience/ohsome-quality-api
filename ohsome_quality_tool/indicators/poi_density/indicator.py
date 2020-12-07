import json
from typing import Dict, Tuple

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.layers import SKETCHMAP_FITNESS_POI_LAYER_COMBINED
from ohsome_quality_tool.utils.label_interpretations import POI_DENSITY_LABEL_INTERPRETATIONS

# threshold values defining the color of the traffic light
# derived directly from sketchmap_fitness repo
THRESHOLD_YELLOW = 30
THRESHOLD_RED = 10


class Indicator(BaseIndicator):
    """The POI Density Indicator."""

    name = "POI_DENSITY"
    description = """
        Derive the density of OSM features
    """
    interpretations: Dict = POI_DENSITY_LABEL_INTERPRETATIONS

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

    def preprocess(self) -> float:
        logger.info(f"run preprocessing for {self.name} indicator")

        query_results = ohsome_api.process_ohsome_api(
            endpoint="elements/count/density/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )

        preprocessing_result = query_results["combined"]["result"][0]["value"]

        return preprocessing_result

    def calculate(
        self, preprocessing_result: float
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")

        result = preprocessing_result
        text = "The density of landmarks (points of reference, e.g. waterbodies, supermarkets, " \
               f"churches, bus stops) is {result} features per square-kilometer."

        #TODO: define a better way to derive the quality value from the result
        if result > THRESHOLD_YELLOW:
            label = TrafficLightQualityLevels.GREEN
            value = 0.75
            text = text + self.interpretations["green"]
        elif THRESHOLD_YELLOW >= result > THRESHOLD_RED:
            label = TrafficLightQualityLevels.YELLOW
            value = 0.5
            text = text + self.interpretations["yellow"]
        else:
            label = TrafficLightQualityLevels.RED
            value = 0.25
            text = text + self.interpretations["red"]

        logger.info(
            "result density value: "
            + str(result)
            + " label: "
            + str(label)
            + " value: "
            + str(value)
            + " text: "
            + text
        )

        return label, value, text, result

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
