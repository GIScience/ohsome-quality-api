import json
import os
import uuid
from typing import Dict, Tuple

import numpy as np
import pygal
from geojson import FeatureCollection
from pygal.style import Style

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import (
    DATA_PATH,
    TrafficLightQualityLevels,
    logger,
)
from ohsome_quality_tool.utils.geodatabase import get_area_of_bpolys
from ohsome_quality_tool.utils.label_interpretations import (
    POI_DENSITY_LABEL_INTERPRETATIONS,
)
from ohsome_quality_tool.utils.layers import SKETCHMAP_FITNESS_POI_LAYER_COMBINED

# threshold values defining the color of the traffic light
# derived directly from sketchmap_fitness repo
THRESHOLD_YELLOW = 30
THRESHOLD_RED = 10


class Indicator(BaseIndicator):
    """The POI Density Indicator."""

    name = "poi-density"
    description = (
        "Derive the density of OSM features "
        "(count divided by area in square-kilometers)"
    )
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

        """
        query_results_density = ohsome_api.process_ohsome_api(
            endpoint="elements/count/density/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )
        """

        # calculate area for polygon
        area_sqkm = get_area_of_bpolys(self.bpolys)

        query_results_count = ohsome_api.process_ohsome_api(
            endpoint="elements/count/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )

        preprocessing_results = {"area_sqkm": area_sqkm}
        # TODO: this indicator currently has only a single layer
        for layer in self.layers.keys():
            preprocessing_results[f"{layer}_count"] = query_results_count[layer][
                "result"
            ][0]["value"]
            preprocessing_results[f"{layer}_density"] = (
                preprocessing_results[f"{layer}_count"] / area_sqkm
            )

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")

        # TODO: we need to think about how we handle this
        #  if there are different layers
        result = preprocessing_results["combined_density"]
        text = (
            "The density of landmarks (points of reference, "
            "e.g. waterbodies, supermarkets, "
            f"churches, bus stops) is {result} features."
        )

        # TODO: define a better way to derive the quality value from the result
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
            f"result density value: {result}, label: {label},"
            f" value: {value}, text: {text}"
        )

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures

        # is it possible to comibine diffrent pygal chart types ie stacked and xy?
        CustomStyle = Style(colors=("green", "yellow", "blue"))
        xy_chart = pygal.XY(stroke=True, style=CustomStyle)

        # set x max value based on area
        if data["area_sqkm"] < 10:
            max_area = 10
        else:
            max_area = round(data["area_sqkm"] * 2 / 10) * 10
        x = np.linspace(0, max_area, 2)

        def greenThresholdFunction(area):
            return THRESHOLD_YELLOW * area

        def yellowThresholdFunction(area):
            return THRESHOLD_RED * area

        xy_chart.add(
            " Green threshold ", [(xi, greenThresholdFunction(xi)) for xi in x]
        )
        xy_chart.add(
            " Yellow threshold ", [(xi, yellowThresholdFunction(xi)) for xi in x]
        )

        xy_chart.add("location", [(data["area_sqkm"], data["combined_count"])])
        xy_chart.title = "POI Density (POIs per Area)"
        xy_chart.x_title = "Area [sqkm]"
        xy_chart.y_title = "POIs"

        if self.dynamic:
            # generate a random ID for the outfile name
            random_id = uuid.uuid1()
            filename = f"{self.name}_{random_id}.svg"
            outfile = os.path.join(DATA_PATH, filename)
        else:
            filename = f"{self.name}_{self.dataset}_{self.feature_id}.svg"
            outfile = os.path.join(DATA_PATH, filename)

        xy_chart.render_to_file(outfile)
        logger.info(f"exported figure: {outfile}")
        return filename
