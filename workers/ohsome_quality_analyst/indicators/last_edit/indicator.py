import json
import logging
from io import StringIO
from string import Template
from typing import Dict

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from geojson import FeatureCollection

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client


class LastEdit(BaseIndicator):
    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = None,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.time_range = time_range
        # TODO: thresholds might be better defined for each OSM layer
        self.threshold_yellow = 20  # more than 20% edited last year --> green
        self.threshold_red = 5  # more than 5% edited last year --> yellow
        self.edited_features = None
        self.total_features = None
        self.share_edited_features = None

    async def preprocess(self) -> Dict:
        if self.time_range is None:
            latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
            self.time_range = "{},{}".format(
                (latest_ohsome_stamp - relativedelta(years=1)).strftime("%Y-%m-%d"),
                latest_ohsome_stamp.strftime("%Y-%m-%d"),
            )

        query_results_contributions = await ohsome_client.query(
            layer=self.layer,
            bpolys=json.dumps(self.bpolys),
            time=self.time_range,
            endpoint="contributions/latest/centroid",
        )
        query_results_totals = await ohsome_client.query(
            layer=self.layer,
            bpolys=json.dumps(self.bpolys),
        )
        try:
            self.edited_features = len(query_results_contributions["features"])
        except KeyError:
            # no feature has been edited in the time range
            self.edited_features = 0

        self.total_features = query_results_totals["result"][0]["value"]
        if self.total_features != 0 and self.total_features is not None:
            if self.edited_features > self.total_features:
                # It can happen that features are counted which has been deleted since.
                self.share_edited_features = 100
            else:
                self.share_edited_features = round(
                    (self.edited_features / self.total_features) * 100
                )

    def calculate(self) -> None:
        description = Template(self.metadata.result_description).substitute(
            share=self.share_edited_features, layer_name=self.layer.name
        )
        if self.total_features == 0 or self.total_features is None:
            label = "undefined"
            value = None
            description = (
                "Since the OHSOME query returned a count of 0 for this feature "
                "a quality estimation can not be made for this filter"
            )
        elif self.share_edited_features >= self.threshold_yellow:
            label = "green"
            value = 1.0
            description += self.metadata.label_description["green"]
        elif self.share_edited_features >= self.threshold_red:
            label = "yellow"
            value = 0.5
            description += self.metadata.label_description["yellow"]
        else:
            label = "red"
            value = 0.0
            description += self.metadata.label_description["red"]

        self.result.label = label
        self.result.value = value
        self.result.description = description

    def create_figure(self) -> None:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        if self.share_edited_features is None:
            return None

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

        for c, s, l in zip(colors, sizes, labels):
            handles.append(mpatches.Patch(color=c, label=f"{l}"))

        # Plot inner Pie (Indicator Value)
        radius = 1 - size
        sizes = (100 - self.share_edited_features, self.share_edited_features)
        colors = ("white", "black")
        ax.pie(
            sizes,
            radius=radius,
            colors=colors,
            startangle=90,
            wedgeprops={"width": size},
        )

        black_patch = mpatches.Patch(
            color="black", label=f"{self.layer.name}: {self.share_edited_features} %"
        )
        handles.append(black_patch)

        ax.legend(handles=handles)
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
