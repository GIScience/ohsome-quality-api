import json
import logging
from io import StringIO
from string import Template

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from geojson import FeatureCollection

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client


class TagsRatio(BaseIndicator):
    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            bpolys=bpolys,
        )
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.ratio = None
        self.count_all = None
        self.count_match = None

    async def preprocess(self) -> bool:

        query_results_count = await ohsome_client.query(
            layer=self.layer, bpolys=json.dumps(self.bpolys), ratio=True
        )
        if query_results_count is None:
            return False
        self.ratio = query_results_count["ratioResult"][0]["ratio"]
        self.count_all = query_results_count["ratioResult"][0]["value"]
        self.count_match = query_results_count["ratioResult"][0]["value2"]
        return True

    def calculate(self) -> bool:
        if isinstance(self.ratio, str) or str(self.ratio) == "None":
            description = Template(self.metadata.result_description).substitute(
                result=self.ratio,
                all=f"{self.count_all}",
                matched=f"{self.count_match}",
            )
            self.result.value = None
            self.result.label = "undefined"
            self.result.description = (
                description + self.metadata.label_description["undefined"]
            )
            return False
        else:
            description = Template(self.metadata.result_description).substitute(
                result=f"{self.ratio:.2f}",
                all=f"{self.count_all}",
                matched=f"{self.count_match}",
            )
            if self.count_all == 0:
                self.result.value = None
                self.result.label = "undefined"
                self.result.description = description + "No features in this region"
                return False
            else:
                if self.ratio >= self.threshold_yellow:
                    self.result.value = 1.0
                    self.result.label = "green"
                    self.result.description = (
                        description + self.metadata.label_description["green"]
                    )
                elif self.threshold_yellow > self.ratio > self.threshold_red:
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
        return True

    def create_figure(self) -> bool:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        if isinstance(self.ratio, str) or str(self.ratio) == "None":
            return False
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
                color="black",
                label=f"{self.layer.name} \nRatio: " f"{round(self.ratio, 2)}",
            )
            handles.append(black_patch)

            ax.legend(handles=handles)
            ax.axis("equal")
            img_data = StringIO()
            plt.savefig(img_data, format="svg", bbox_inches="tight")
            self.result.svg = img_data.getvalue()
            logging.info(f"Got svg-figure string for indicator {self.metadata.name}")
            plt.close("all")
        return True
