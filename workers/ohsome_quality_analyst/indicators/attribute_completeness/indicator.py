import logging
from io import StringIO
from string import Template

import dateutil.parser
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from geojson import Feature

from ohsome_quality_analyst.indicators.base import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.topics.models import BaseTopic as Topic


class AttributeCompleteness(BaseIndicator):
    # TODO make attribute a list
    def __init__(self, topic: Topic, feature: Feature, attribute) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.attribute = attribute
        self.ratio = None
        self.absolute_value_1 = None
        self.absolute_value_2 = None

    async def preprocess(self) -> None:
        # Get attribute filter
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            attribute=self.attribute,
            ratio=True,
        )
        timestamp = response["ratioResult"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        self.ratio = response["ratioResult"][0]["ratio"]
        self.absolute_value_1 = response["ratioResult"][0]["value"]
        self.absolute_value_2 = response["ratioResult"][0]["value2"]

    def calculate(self) -> None:
        # self.result.value (ratio) can be of type float, NaN if no features of filter1
        # are in the region or None if the topic has no filter2
        if self.result.value == "NaN" or self.result.value is None:
            self.result.value = None
            return
        description = Template(self.metadata.result_description).substitute(
            result=round(self.result.value, 1),
            all=round(self.count_all, 1),
            matched=round(self.count_match, 1),
        )
        if self.count_all == 0:
            self.result.description = description + "No features in this region"
            return

        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        elif self.threshold_yellow > self.result.value >= self.threshold_red:
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
        if type(self.result.value) == str:
            sizes = (0, 1)
        else:
            sizes = (1 - self.result.value, self.result.value)
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
            label=f"{self.topic.name} \nRatio: {round(self.result.value, 2)}",
        )
        handles.append(black_patch)

        ax.legend(handles=handles)
        ax.axis("equal")
        img_data = StringIO()
        plt.tight_layout()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()
        plt.close("all")
