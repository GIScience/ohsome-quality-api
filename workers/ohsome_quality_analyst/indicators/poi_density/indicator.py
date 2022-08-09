import logging
from io import StringIO
from string import Template

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.geodatabase.client import get_area_of_bpolys
from ohsome_quality_analyst.ohsome import client as ohsome_client

# threshold values defining the color of the traffic light
# derived directly from sketchmap_fitness repo


class PoiDensity(BaseIndicator):
    def __init__(self, layer: Layer, feature: Feature) -> None:
        super().__init__(layer=layer, feature=feature)
        self.threshold_yellow = 30
        self.threshold_red = 10
        self.area_sqkm = None
        self.count = None

    def green_threshold_function(self, area):
        return self.threshold_yellow * area

    def yellow_threshold_function(self, area):
        return self.threshold_red * area

    async def preprocess(self) -> None:
        query_results_count = await ohsome_client.query(self.layer, self.feature)
        self.area_sqkm = await get_area_of_bpolys(self.feature.geometry)
        self.count = query_results_count["result"][0]["value"]
        timestamp = query_results_count["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)

    def calculate(self) -> None:
        # TODO: we need to think about how we handle this
        #  if there are different layers
        self.result.value = self.count / self.area_sqkm  # density
        description = Template(self.metadata.result_description).substitute(
            result=f"{self.result.value:.2f}"
        )
        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        else:
            if self.result.value > self.threshold_red:
                self.result.class_ = 3
                self.result.description = (
                    description + self.metadata.label_description["yellow"]
                )
            else:
                self.result.class_ = 1
                self.result.description = (
                    description + self.metadata.label_description["red"]
                )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("POI Density (POIs per Area)")
        ax.set_xlabel("Area [$km^2$]")
        ax.set_ylabel("POIs")

        # Set x max value based on area
        if self.area_sqkm < 10:
            max_area = 10
        else:
            max_area = round(self.area_sqkm * 2 / 10) * 10
        x = np.linspace(0, max_area, 2)

        # Plot thresholds as line.
        y1 = [self.green_threshold_function(xi) for xi in x]
        y2 = [self.yellow_threshold_function(xi) for xi in x]

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
        ax.fill_between(x, y1, max(max(y1), self.count), alpha=0.5, color="green")

        # Plot point as circle ("o").
        ax.plot(
            self.area_sqkm,
            self.count,
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        plt.close("all")
