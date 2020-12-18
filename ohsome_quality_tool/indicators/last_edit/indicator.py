import json
from typing import Dict, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import (
    LayerDefinition,
    TrafficLightQualityLevels,
    logger,
)
from ohsome_quality_tool.utils.layers import BUILDING_COUNT_LAYER

# TODO: thresholds might be better defined for each OSM layer
THRESHOLD_YELLOW = 0.20  # more than 20% edited last year --> green
THRESHOLD_RED = 0.05  # more than 5% edited last year --> yellow


class Indicator(BaseIndicator):
    """The Last Edit Indicator."""

    name = "last-edit"
    description = """
        Check the percentage of features that have been edited in the past two years.
    """

    def __init__(
        self,
        dynamic: bool,
        layer: LayerDefinition = BUILDING_COUNT_LAYER,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = "2019-07-15,2020-07-15",
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layer=layer,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.time_range = time_range

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

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

        edited_features = len(query_results_contributions["features"])
        total_features = query_results_totals["result"][0]["value"]

        preprocessing_results = {
            "edited_features": edited_features,
            "total_features": total_features,
            "share_edited_features": edited_features / total_features,
        }

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")

        if preprocessing_results["share_edited_features"] >= THRESHOLD_YELLOW:
            label = TrafficLightQualityLevels.GREEN
        elif preprocessing_results["share_edited_features"] >= THRESHOLD_RED:
            label = TrafficLightQualityLevels.YELLOW
        else:
            label = TrafficLightQualityLevels.RED

        share = round(preprocessing_results["share_edited_features"] * 100)
        text = (
            f"{share}% of the {self.layer.name} in OSM have been edited "
            "during the last year. "
            f"This corresponds to a {label.name} label in regard to data quality.\n\n"
        )
        value = label.value

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
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
        labels = colors
        ax.pie(
            sizes,
            radius=radius,
            colors=colors,
            # autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"width": size, "alpha": 0.5},
        )

        for c, s, l in zip(colors, sizes, labels):
            handles.append(mpatches.Patch(color=c, label=f"{l}: {s} %"))

        # Plot inner Pie (Indicator Value)
        radius = 1 - size
        share_edited_features = int(data["share_edited_features"] * 100)
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

        plt.savefig(self.outfile, format="svg")
        plt.close("all")
        logger.info(f"saved plot: {self.filename}")
        return self.filename
