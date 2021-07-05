import json
import logging
from io import StringIO
from string import Template

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from geojson import FeatureCollection

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client


class LastEdit(BaseIndicator):
    """Ratio of latest contribution count to element count."""

    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
        time_range: str = None,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            bpolys=bpolys,
        )
        self.threshold_yellow = 20  # more than 20% edited last year --> green
        self.threshold_red = 5

        self.time_range = time_range
        self.element_count = None
        self.contributions_latest_count = None
        self.ratio = None  # Ratio of latest contribution count to element count

    async def preprocess(self) -> bool:
        if self.time_range is None:
            latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
            self.time_range = "{start},{end}".format(
                start=(latest_ohsome_stamp - relativedelta(years=1)).strftime(
                    "%Y-%m-%d"
                ),
                end=latest_ohsome_stamp.strftime("%Y-%m-%d"),
            )

        response = await ohsome_client.query(
            layer=self.layer,
            bpolys=json.dumps(self.bpolys),
            time=self.time_range,
            endpoint="contributions/latest/count",
        )
        self.contributions_latest_count = response["result"][0]["value"]
        response = await ohsome_client.query(
            layer=self.layer,
            bpolys=json.dumps(self.bpolys),
        )
        self.element_count = response["result"][0]["value"]

        return True

    def calculate(self) -> bool:
        logging.info(f"Calculation for indicator: {self.metadata.name}")

        # It can be that features are counted, but have been deleted since.
        if self.element_count == 0:
            self.result.label = "undefined"
            self.result.value = None
            self.result.description = "In the AOI no features are present."
            return False

        if self.contributions_latest_count > self.element_count:
            self.ratio = 100
        else:
            self.ratio = round(
                (self.contributions_latest_count / self.element_count) * 100
            )

        description = Template(self.metadata.result_description).substitute(
            share=self.contributions_latest_count, layer_name=self.layer.name
        )

        if self.ratio >= self.threshold_yellow:
            self.result.label = "green"
            self.result.value = 1.0
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        elif self.ratio >= self.threshold_red:
            self.result.label = "yellow"
            self.result.value = 0.5
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
        elif self.ratio < self.threshold_red:
            self.result.label = "red"
            self.result.value = 0.0
            self.result.description = (
                description + self.metadata.label_description["red"]
            )

        return True

    def create_figure(self) -> bool:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Features Edited Last Year")

        size = 0.3  # Width of the pie
        handles = []  # Handles for legend

        # Plot outer Pie (Traffic Light)
        radius = 1
        sizes = [80, 15, 5]
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

        for c, l in zip(colors, labels):
            handles.append(mpatches.Patch(color=c, label=f"{l}"))

        # Plot inner Pie (Indicator Value)
        radius = 1 - size
        sizes = (100 - self.ratio, self.ratio)
        colors = ("white", "black")
        ax.pie(
            sizes,
            radius=radius,
            colors=colors,
            startangle=90,
            wedgeprops={"width": size},
        )

        black_patch = mpatches.Patch(
            color="black", label=f"{self.layer.name}: {self.ratio} %"
        )
        handles.append(black_patch)

        ax.legend(handles=handles)
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
        return True
