import logging
from io import StringIO
from string import Template
from typing import Optional, Tuple

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.definitions import get_attribution, get_raster_dataset
from ohsome_quality_analyst.geodatabase.client import get_area_of_bpolys
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.raster.client import get_zonal_stats


class GhsPopComparisonRoads(BaseIndicator):
    """Set number of features and population into perspective."""

    def __init__(
        self,
        layer: Layer,
        feature: Feature,
        thresholds: Optional[Tuple[dict, dict, dict, dict]] = None,
    ) -> None:
        super().__init__(layer=layer, feature=feature, thresholds=thresholds)
        # Those attributes will be set during lifecycle of the object.
        self.pop_count = None
        self.area = None
        self.pop_count_per_sqkm = None
        self.feature_length = None

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])

    def green_threshold_function(self, pop_per_sqkm) -> float:
        """Return road density threshold for green label."""
        if pop_per_sqkm < 5000:
            return pop_per_sqkm / self.thresholds[2]["a"]
        else:
            return 10

    def yellow_threshold_function(self, pop_per_sqkm) -> float:
        """Return road density threshold for yellow label."""
        if pop_per_sqkm < 5000:
            return pop_per_sqkm / self.thresholds[0]["a"]
        else:
            return 5

    async def preprocess(self) -> None:
        raster = get_raster_dataset("GHS_POP_R2019A")
        pop_count = get_zonal_stats(self.feature, raster, stats="sum")[0]["sum"]
        area = await get_area_of_bpolys(self.feature.geometry)
        if pop_count is None:
            pop_count = 0
        self.area = area
        self.pop_count = pop_count

        query_results = await ohsome_client.query(self.layer, self.feature)
        # results in meter, we need km
        self.feature_length = query_results["result"][0]["value"] / 1000
        timestamp = query_results["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)

    def calculate(self) -> None:
        self.pop_count_per_sqkm = self.pop_count / self.area
        self.result.value = self.feature_length / self.area  # feature_length_per_sqkm
        description = Template(self.metadata.result_description).substitute(
            pop_count=round(self.pop_count),
            area=round(self.area, 1),
            pop_count_per_sqkm=round(self.pop_count_per_sqkm, 1),
            feature_length_per_sqkm=round(self.result.value, 1),
        )

        green_road_density = self.green_threshold_function(self.pop_count_per_sqkm)
        yellow_road_density = self.yellow_threshold_function(self.pop_count_per_sqkm)

        if self.pop_count_per_sqkm == 0:
            return
        # road density is compliant to the green values or even higher
        elif self.result.value >= green_road_density:
            self.result.class_ = 5
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        # road density is compliant to the yellow values
        # we assume there could be more roads mapped
        elif self.result.value >= yellow_road_density:
            self.result.class_ = 3
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
        # road density is too small, none, or too short roads
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

        ax.set_title("Road density against \npeople per $km^2$")
        ax.set_xlabel("Population Density [$1/km^2$]")
        ax.set_ylabel("Road density [$km/km^2$]")

        # Set x max value based on area
        if self.pop_count_per_sqkm < 100:
            max_area = 10
        else:
            max_area = round(self.pop_count_per_sqkm * 2 / 10) * 10
        x = np.linspace(0, max_area, 100)
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
        ax.fill_between(
            x,
            y1,
            max(max(y1), self.result.value),
            alpha=0.5,
            color="green",
        )

        # Plot pont as circle ("o").
        ax.plot(
            self.pop_count_per_sqkm,
            self.result.value,
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()
        plt.close("all")
