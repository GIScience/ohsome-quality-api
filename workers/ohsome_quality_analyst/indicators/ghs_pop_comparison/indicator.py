import json
import logging
from io import StringIO
from string import Template

import matplotlib.pyplot as plt
import numpy as np
from geojson import FeatureCollection

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.ohsome import client as ohsome_client


class GhsPopComparison(BaseIndicator):
    """Set number of features and population into perspective."""

    def __init__(
        self,
        layer_name: str,
        dataset: str = None,
        feature_id: int = None,
        bpolys: FeatureCollection = None,
    ) -> None:
        super().__init__(
            dataset=dataset,
            feature_id=feature_id,
            layer_name=layer_name,
            bpolys=bpolys,
        )
        # Those attributes will be set during lifecycle of the object.
        self.pop_count = None
        self.area = None
        self.pop_count_per_sqkm = None
        self.feature_count = None
        self.feature_count_per_sqkm = None

    def greenThresholdFunction(self, pop_per_sqkm):
        # TODO: Add docstring
        # TODO: adjust threshold functions
        # more precise values? maybe as fraction of the threshold functions?
        return 5 * np.sqrt(pop_per_sqkm)

    def yellowThresholdFunction(self, pop_per_sqkm):
        # TODO: Add docstring
        # TODO: adjust threshold functions
        # more precise values? maybe as fraction of the threshold functions?
        return 0.75 * np.sqrt(pop_per_sqkm)

    async def preprocess(self):
        pop_count, area = db_client.get_zonal_stats_population(bpolys=self.bpolys)

        if pop_count is None:
            pop_count = 0
        self.area = area
        self.pop_count = pop_count

        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=json.dumps(self.bpolys)
        )
        self.feature_count = query_results["result"][0]["value"]
        self.feature_count_per_sqkm = self.feature_count / self.area
        self.pop_count_per_sqkm = self.pop_count / self.area

    def calculate(self):
        description = Template(self.metadata.result_description).substitute(
            pop_count=round(self.pop_count),
            area=round(self.area, 1),
            pop_count_per_sqkm=round(self.pop_count_per_sqkm, 1),
            feature_count_per_sqkm=round(self.feature_count_per_sqkm, 1),
        )

        if self.pop_count_per_sqkm == 0:
            label = "undefined"
            value = None
            description += self.metadata.label_description["undefined"]

        elif self.feature_count_per_sqkm <= self.yellowThresholdFunction(
            self.pop_count_per_sqkm
        ):
            value = (
                self.feature_count_per_sqkm
                / self.yellowThresholdFunction(self.pop_count_per_sqkm)
            ) * (0.5)
            description += self.metadata.label_description["red"]
            label = "red"

        elif self.feature_count_per_sqkm <= self.greenThresholdFunction(
            self.pop_count_per_sqkm
        ):
            green = self.greenThresholdFunction(self.pop_count_per_sqkm)
            yellow = self.yellowThresholdFunction(self.pop_count_per_sqkm)
            fraction = (self.feature_count_per_sqkm - yellow) / (green - yellow) * 0.5
            value = 0.5 + fraction
            description += self.metadata.label_description["yellow"]
            label = "yellow"

        else:
            value = 1.0
            description += self.metadata.label_description["green"]
            label = "green"

        self.result.label = label
        self.result.value = value
        self.result.description = description

    def create_figure(self):
        if self.result.label == "undefined":
            logging.info("Skipping figure creation.")
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
        y1 = [self.greenThresholdFunction(xi) for xi in x]
        y2 = [self.yellowThresholdFunction(xi) for xi in x]
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
