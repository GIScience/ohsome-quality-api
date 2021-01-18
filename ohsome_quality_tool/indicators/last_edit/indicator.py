import json
from string import Template
from typing import Dict

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger


class LastEdit(BaseIndicator):
    def __init__(
        self,
        dynamic: bool,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        # TODO: adjust time range here to always use last year
        time_range: str = "2019-07-15,2020-07-15",
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layer_name=layer_name,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.time_range = time_range
        # TODO: thresholds might be better defined for each OSM layer
        self.threshold_yellow = 0.20  # more than 20% edited last year --> green
        self.threshold_red = 0.05  # more than 5% edited last year --> yellow
        self.edited_features = None
        self.total_features = None
        self.share_edited_features = None

    def preprocess(self) -> Dict:
        logger.info(f"Preprocessing for indicator: {self.metadata.name}")

        query_results_contributions = ohsome_api.query_ohsome_api(
            endpoint="contributions/latest/centroid/",
            filter_string=self.layer.filter,
            bpolys=json.dumps(self.bpolys),
            time=self.time_range,
        )

        query_results_totals = ohsome_api.query_ohsome_api(
            endpoint="elements/count/",
            filter_string=self.layer.filter,
            bpolys=json.dumps(self.bpolys),
        )

        try:
            self.edited_features = len(query_results_contributions["features"])
        except KeyError:
            # no feature has been edited in the time range
            self.edited_features = 0

        self.total_features = query_results_totals["result"][0]["value"]
        self.share_edited_features = (
            (self.edited_features / self.total_features)
            if self.total_features != 0
            else -1
        )

    def calculate(self):
        logger.info(f"Calculation for indicator: {self.metadata.name}")

        share = round(self.share_edited_features * 100)
        description = Template(self.metadata.result_description).substitute(
            share=share, layer_name=self.layer.name
        )
        if self.share_edited_features == -1:
            label = TrafficLightQualityLevels.UNDEFINED
            value = -1.0
            description = (
                "Since the OHSOME query returned a count of 0 for this feature "
                "a quality estimation can not be made for this filter"
            )
        elif self.share_edited_features >= self.threshold_yellow:
            label = TrafficLightQualityLevels.GREEN
            value = 1.0
            description += self.metadata.label_description["green"]
        elif self.share_edited_features >= self.threshold_red:
            label = TrafficLightQualityLevels.YELLOW
            value = 0.5
            description += self.metadata.label_description["yellow"]
        else:
            label = TrafficLightQualityLevels.RED
            value = 0.0
            description += self.metadata.label_description["red"]

        self.result.label = label
        self.result.value = value
        self.result.description = description

    def create_figure(self):
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        logger.info(f"Create firgure for indicator: {self.metadata.name}")

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Features Edited Last Year")
        # ax.set_xlabel("Edited [%]")
        # ax.set_ylabel("OpenStreetMap [%]")

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
            # autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"width": size, "alpha": 0.5},
        )

        for c, s, l in zip(colors, sizes, labels):
            handles.append(mpatches.Patch(color=c, label=f"{l}"))

        # Plot inner Pie (Indicator Value)
        radius = 1 - size
        share_edited_features = int(self.share_edited_features * 100)
        sizes = (100 - share_edited_features, share_edited_features)
        colors = ("white", "black")
        ax.pie(
            sizes,
            radius=radius,
            colors=colors,
            # autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"width": size},
        )

        black_patch = mpatches.Patch(
            color="black", label=f"{self.layer.name}: {share_edited_features} %"
        )
        handles.append(black_patch)

        ax.legend(handles=handles)
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

        # # TODO: Decide which plot type to use. Pi chart or bar chart?
        # # Plot as bar chart
        # px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        # figsize = (400 * px, 400 * px)
        # fig = plt.figure(figsize=figsize)
        # ax = fig.add_subplot()

        # ax.set_title("Features Edited Last Year")

        # ax.set_ylim((0, 100))

        # threshold_yellow = 20  # more than 20% edited last year --> green
        # threshold_red = 5

        # x = [-1, 1]
        # y1 = [threshold_yellow, threshold_yellow]
        # y2 = [threshold_red, threshold_red]

        # # Plot thresholds as line.
        # line = line = ax.plot(
        #     x,
        #     y1,
        #     color="black",
        #     label="Threshold A",
        # )
        # plt.setp(line, linestyle="--")

        # line = ax.plot(
        #     x,
        #     y2,
        #     color="black",
        #     label="Threshold B",
        # )
        # plt.setp(line, linestyle=":")
        # ax.fill_between(x, y2, 0, alpha=0.5, color="red")
        # ax.fill_between(x, y2, y1, alpha=0.5, color="yellow")
        # ax.fill_between(x, y1, 100, alpha=0.5, color="green")

        # y_data = int(data["share_edited_features"] * 100)
        # ax.bar("self.layer.name", y_data, color="black", label=self.layer.name)

        # # ax.plot(x_data, y_data, "o", color="black", label=self.layer.name)

        # ax.legend()

        logger.info(
            f"Save figure for indicator: {self.metadata.name}\n to: {self.result.svg}"
        )
        plt.savefig(self.result.svg, format="svg")
        plt.close("all")
