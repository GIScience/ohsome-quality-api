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
from ohsome_quality_analyst.raster.client import get_zonal_stats
from ohsome_quality_analyst.utils.definitions import get_attribution, get_raster_dataset


class GhsPopComparisonBuildings(BaseIndicator):
    """Set number of features and population into perspective."""

    def __init__(
        self,
        layer: Layer,
        feature: Feature,
    ) -> None:
        super().__init__(
            layer=layer,
            feature=feature,
        )
        # Those attributes will be set during lifecycle of the object.
        self.pop_count = None
        self.area = None
        self.pop_count_per_sqkm = None
        self.feature_count = None
        self.feature_count_per_sqkm = None

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])

    def green_threshold_function(self, pop_per_sqkm) -> float:
        # TODO: Add docstring
        # TODO: adjust threshold functions
        # more precise values? maybe as fraction of the threshold functions?
        return 5.0 * np.sqrt(pop_per_sqkm)

    def yellow_threshold_function(self, pop_per_sqkm) -> float:
        # TODO: Add docstring
        # TODO: adjust threshold functions
        # more precise values? maybe as fraction of the threshold functions?
        return 0.75 * np.sqrt(pop_per_sqkm)

    async def preprocess(self) -> None:
        raster = get_raster_dataset("GHS_POP_R2019A")
        pop_count = get_zonal_stats(self.feature, raster, stats="sum")[0]["sum"]
        area = await get_area_of_bpolys(self.feature.geometry)

        if pop_count is None:
            pop_count = 0
        self.area = area
        self.pop_count = pop_count

        query_results = await ohsome_client.query(self.layer, self.feature.geometry)
        self.feature_count = query_results["result"][0]["value"]
        timestamp = query_results["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        self.feature_count_per_sqkm = self.feature_count / self.area
        self.pop_count_per_sqkm = self.pop_count / self.area

    def calculate(self) -> None:
        description = Template(self.metadata.result_description).substitute(
            pop_count=round(self.pop_count),
            area=round(self.area, 1),
            pop_count_per_sqkm=round(self.pop_count_per_sqkm, 1),
            feature_count_per_sqkm=round(self.feature_count_per_sqkm, 1),
        )

        if self.pop_count_per_sqkm == 0:
            return

        elif self.feature_count_per_sqkm <= self.yellow_threshold_function(
            self.pop_count_per_sqkm
        ):
            self.result.value = (
                self.feature_count_per_sqkm
                / self.yellow_threshold_function(self.pop_count_per_sqkm)
            ) * (0.5)
            self.result.description = (
                description + self.metadata.label_description["red"]
            )
            self.result.label = "red"

        elif self.feature_count_per_sqkm <= self.green_threshold_function(
            self.pop_count_per_sqkm
        ):
            green = self.green_threshold_function(self.pop_count_per_sqkm)
            yellow = self.yellow_threshold_function(self.pop_count_per_sqkm)
            fraction = (self.feature_count_per_sqkm - yellow) / (green - yellow) * 0.5
            self.result.value = 0.5 + fraction
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
            self.result.label = "yellow"

        else:
            self.result.value = 1.0
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
            self.result.label = "green"

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Buildings per person against people per $km^2$")
        ax.set_xlabel("Population Density [$1/km^2$]")
        ax.set_ylabel("Building Density [$1/km^2$]")

        # Set x max value based on area
        if self.pop_count_per_sqkm < 100:
            max_area = 10
        else:
            max_area = round(self.pop_count_per_sqkm * 2 / 10) * 10
        x = np.linspace(0, max_area, 20)

        # Plot thresholds as line.
        y1 = [self.green_threshold_function(xi) for xi in x]
        y2 = [self.yellow_threshold_function(xi) for xi in x]
        line = line = ax.plot(
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
        ax.fill_between(
            x,
            y1,
            max(max(y1), self.feature_count_per_sqkm),
            alpha=0.5,
            color="green",
        )

        # Plot pont as circle ("o").
        ax.plot(
            self.pop_count_per_sqkm,
            self.feature_count_per_sqkm,
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
