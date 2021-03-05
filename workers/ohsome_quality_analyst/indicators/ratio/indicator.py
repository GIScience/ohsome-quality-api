import json
import logging
from io import StringIO
from string import Template
from typing import Dict

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import requests
from geojson import FeatureCollection

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.utils.definitions import OHSOME_API


def query_ratio_count(
    layer, bpolys: str, time: str = None, endpoint: str = None
) -> Dict:
    """Query ohsome API endpoint with filter."""
    if endpoint:
        url = OHSOME_API + endpoint
    else:
        url = OHSOME_API + layer.endpoint
    data = {
        "bpolys": bpolys,
        "filter": layer.filter,
        "filter2": layer.filter2,
        "time": time,
    }
    response = requests.post(url, data=data)

    logging.info("Query ohsome API.")
    logging.info("Query URL: " + url)
    logging.info("Query Filter: " + layer.filter)
    if response.status_code == 200:
        logging.info("Query successful!")
    elif response.status_code == 404:
        logging.info("Query failed!")

    return response.json()


class Ratio(BaseIndicator):
    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.threshold_yellow = 75
        self.threshold_red = 25
        self.ratio = None
        self.count_all = None
        self.count_match = None

    def preprocess(self):
        logging.info(f"Preprocessing for indicator: {self.metadata.name}")

        query_results_count = query_ratio_count(
            layer=self.layer, bpolys=json.dumps(self.bpolys)
        )

        self.ratio = query_results_count["ratioResult"][0]["ratio"]
        self.count_all = query_results_count["ratioResult"][0]["value"]
        self.count_match = query_results_count["ratioResult"][0]["value2"]

    def calculate(self):
        logging.info(f"Calculation for indicator: {self.metadata.name}")

        if type(self.ratio) == str:
            description = Template(self.metadata.result_description).substitute(
                result=self.ratio,
                all=f"{self.count_all}",
                matched=f"{self.count_match}",
            )
        else:
            description = Template(self.metadata.result_description).substitute(
                result=f"{self.ratio:.2f}",
                all=f"{self.count_all}",
                matched=f"{self.count_match}",
            )

        if type(self.ratio) is not str:
            if self.count_all == 0:
                self.result.value = None
                self.result.label = "undefined"
                self.result.description = description + "No features in this region"
            else:
                if self.ratio >= self.threshold_yellow:
                    self.result.value = 1.0
                    self.result.label = "green"
                    self.result.description = (
                        description + self.metadata.label_description["green"]
                    )
                elif self.threshold_yellow > self.ratio < self.threshold_red:
                    self.result.value = 0.5
                    self.result.label = "yellow"
                    self.result.description = (
                        description + self.metadata.label_description["yellow"]
                    )
                else:
                    self.result.value = 0.0
                    self.result.label = "red"
                    self.result.description = (
                        description + self.metadata.label_description["red"]
                    )
        else:
            self.result.value = None
            self.result.label = "undefined"
            self.result.description = (
                description + self.metadata.label_description["undefined"]
            )

    def create_figure(self, id) -> None:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        logging.info(f"Create firgure for indicator: {self.metadata.name}")

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        if self.ratio is None:
            ax.set_title("Could not calculate indicator")
            img_data = StringIO()
            plt.savefig(img_data, format="svg")
            plt.savefig(
                "test_ratio_jrc" + id + ".png", format="png", bbox_inches="tight"
            )
            self.result.svg = img_data.getvalue()  # this is svg data
            logging.info(f"Got svg-figure string for indicator {self.metadata.name}")
            plt.close("all")
        elif self.ratio == "NaN":
            ax.set_title("No features in this region with given tags")
            img_data = StringIO()
            plt.savefig(img_data, format="svg")
            plt.savefig(
                "test_ratio_jrc" + id + ".png", format="png", bbox_inches="tight"
            )
            self.result.svg = img_data.getvalue()  # this is svg data
            logging.info(f"Got svg-figure string for indicator {self.metadata.name}")
            plt.close("all")
        else:
            ax.set_title(
                "Ratio between all features ("
                + str(self.count_all)
                + ")"
                + "\nand filtered ones ("
                + str(self.count_match)
                + ")"
            )

            size = 0.3  # Width of the pie
            handles = []  # Handles for legend

            # Plot outer Pie (Traffic Light)
            radius = 1
            sizes = [0.25, 0.50, 0.25]
            colors = ["green", "yellow", "red"]
            # TODO: Definie label names.
            labels = ["Good", "Medium", "Bad"]
            ax.pie(
                sizes,
                radius=radius,
                colors=colors,
                startangle=90,
                wedgeprops={"width": size, "alpha": 0.5},
            )

            for c, s, l in zip(colors, sizes, labels):
                handles.append(mpatches.Patch(color=c, label=f"{l}"))

            # Plot inner Pie (Indicator Value)
            radius = 1 - size
            if type(self.ratio) == str:
                sizes = (1 - 1, 1)
            else:
                sizes = (1 - self.ratio, self.ratio)
            colors = ("white", "black")
            ax.pie(
                sizes,
                radius=radius,
                colors=colors,
                startangle=90,
                wedgeprops={"width": size},
            )

            black_patch = mpatches.Patch(
                color="black", label=f"{self.layer.name}: {self.ratio}"
            )
            handles.append(black_patch)

            ax.legend(handles=handles)
            ax.axis(
                "equal"
            )  # Equal aspect ratio ensures that pie is drawn as a circle.

            img_data = StringIO()
            plt.savefig(img_data, format="svg", bbox_inches="tight")
            plt.savefig(
                "test_ratio_jrc" + id + ".png", format="png", bbox_inches="tight"
            )
            # plt.savefig("test_ratio_jrc.png", format="png", bbox_inches="tight")
            self.result.svg = img_data.getvalue()  # this is svg data
            logging.info(f"Got svg-figure string for indicator {self.metadata.name}")
            plt.close("all")
