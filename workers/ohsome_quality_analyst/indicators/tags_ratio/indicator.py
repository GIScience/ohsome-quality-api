import logging
from io import StringIO
from string import Template

import dateutil.parser
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.ohsome import client as ohsome_client


class TagsRatio(BaseIndicator):
    def __init__(self, layer: Layer, feature: Feature) -> None:
        super().__init__(layer=layer, feature=feature)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.ratio = None
        self.count_all = None
        self.count_match = None

    async def preprocess(self) -> None:
        query_results_count = await ohsome_client.query(
            self.layer,
            self.feature.geometry,
            ratio=True,
        )
        self.ratio = query_results_count["ratioResult"][0]["ratio"]
        self.count_all = query_results_count["ratioResult"][0]["value"]
        self.count_match = query_results_count["ratioResult"][0]["value2"]
        timestamp = query_results_count["ratioResult"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)

    def calculate(self) -> None:
        # self.ratio can be of type float, NaN if no features of filter1 are in the
        # region or None if the layer has no filter2
        if self.ratio == "NaN" or self.ratio is None:
            return
        description = Template(self.metadata.result_description).substitute(
            result=round(self.ratio, 1),
            all=round(self.count_all, 1),
            matched=round(self.count_match, 1),
        )
        if self.count_all == 0:
            self.result.description = description + "No features in this region"
            return

        if self.ratio >= self.threshold_yellow:
            self.result.value = 1.0
            self.result.label = "green"
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        elif self.threshold_yellow > self.ratio >= self.threshold_red:
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

    def create_figure(self) -> None:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Ratio between all features and filtered ones")

        size = 0.3  # Width of the pie
        handles = []  # Handles for legend

        # Plot outer Pie (Traffic Light)
        radius = 1
        sizes = [0.25, 0.50, 0.25]
        colors = ["green", "yellow", "red"]
        labels = ["Good", "Medium", "Bad"]
        ax.pie(
            sizes,
            radius=radius,
            colors=colors,
            startangle=90,
            wedgeprops={"width": size, "alpha": 0.5},
        )

        for c, l in zip(colors, labels):
            handles.append(mpatches.Patch(color=c, label=f"{l}"))

        # Plot inner Pie (Indicator Value)
        radius = 1 - size
        if type(self.ratio) == str:
            sizes = (0, 1)
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
            color="black",
            label=f"{self.layer.name} \nRatio: {round(self.ratio, 2)}",
        )
        handles.append(black_patch)

        ax.legend(handles=handles)
        ax.axis("equal")
        img_data = StringIO()
        plt.tight_layout()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()
        logging.info(f"Got svg-figure string for indicator {self.metadata.name}")
        plt.close("all")
