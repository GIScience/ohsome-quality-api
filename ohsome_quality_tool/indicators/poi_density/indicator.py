import json
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.geodatabase import get_area_of_bpolys
from ohsome_quality_tool.utils.label_interpretations import (
    POI_DENSITY_LABEL_INTERPRETATIONS,
)

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
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layer_name=layer_name,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        # calculate area for polygon
        area_sqkm = get_area_of_bpolys(self.bpolys)

        query_results_count = ohsome_api.query_ohsome_api(
            endpoint="elements/count/",
            filter_string=self.layer.filter,
            bpolys=json.dumps(self.bpolys),
        )

        count = query_results_count["result"][0]["value"]
        density = count / area_sqkm

        preprocessing_results = {
            "area_sqkm": area_sqkm,
            "count": count,
            "density": density,
        }

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")

        # TODO: we need to think about how we handle this
        #  if there are different layers
        result = preprocessing_results["density"]
        text = (
            "The density of landmarks (points of reference, "
            "e.g. waterbodies, supermarkets, "
            f"churches, bus stops) is {result:.2f} features per sqkm."
        )

        if result >= THRESHOLD_YELLOW:
            value = 1.0
            label = TrafficLightQualityLevels.GREEN
            text = text + self.interpretations["green"]
        else:
            value = result / THRESHOLD_YELLOW
            if result > THRESHOLD_RED:
                label = TrafficLightQualityLevels.YELLOW
                text = text + self.interpretations["yellow"]
            else:
                label = TrafficLightQualityLevels.RED
                text = text + self.interpretations["red"]

        logger.info(
            f"result density value: {result}, label: {label},"
            f" value: {value}, text: {text}"
        )

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        def greenThresholdFunction(area):
            return THRESHOLD_YELLOW * area

        def yellowThresholdFunction(area):
            return THRESHOLD_RED * area

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("POI Density (POIs per Area)")
        ax.set_xlabel("Area [$km^2$]")
        ax.set_ylabel("POIs")

        # Set x max value based on area
        if data["area_sqkm"] < 10:
            max_area = 10
        else:
            max_area = round(data["area_sqkm"] * 2 / 10) * 10
        x = np.linspace(0, max_area, 2)

        # Plot thresholds as line.
        y1 = [greenThresholdFunction(xi) for xi in x]
        y2 = [yellowThresholdFunction(xi) for xi in x]

        line = ax.plot(
            x,
            y1,
            color="black",
            label="Threshold A",
        )
        plt.setp(line, linestyle="--")

        line = ax.plot(
            x,
            y2,
            color="black",
            label="Threshold B",
        )
        plt.setp(line, linestyle=":")

        # Fill in space between thresholds
        ax.fill_between(x, y2, 0, alpha=0.5, color="red")
        ax.fill_between(x, y1, y2, alpha=0.5, color="yellow")
        ax.fill_between(x, y1, max(max(y1), data["count"]), alpha=0.5, color="green")

        # Plot point as circle ("o").
        ax.plot(
            data["area_sqkm"],
            data["count"],
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        plt.savefig(self.outfile, format="svg")
        logger.info(f"export figures for {self.name} indicator")
        return self.filename
