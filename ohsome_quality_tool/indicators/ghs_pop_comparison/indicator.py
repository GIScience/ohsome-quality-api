import json
from string import Template

import matplotlib.pyplot as plt
import numpy as np
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.ohsome import client as ohsome_client
from ohsome_quality_tool.utils import geodatabase
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger


class GhsPopComparison(BaseIndicator):
    """Set number of features and population into perspective."""

    def __init__(
        self,
        dynamic: bool,
        layer_name: str,
        dataset: str = None,
        feature_id: int = None,
        bpolys: FeatureCollection = None,
    ) -> None:
        super().__init__(
            dataset=dataset,
            feature_id=feature_id,
            dynamic=dynamic,
            layer_name=layer_name,
            bpolys=bpolys,
        )
        self.pop_count = None
        self.area = None
        self.pop_count_per_sqkm = None
        self.feature_count = None
        self.feature_count_per_pop = None
        self.feature_count_per_sqkm = None

    def preprocess(self):
        logger.info(f"Preprocessing for indicator: {self.metadata.name}")

        # if self.dynamic:
        self.pop_count, self.area = geodatabase.get_zonal_stats_population(
            bpolys=self.bpolys
        )
        # else:
        #    pop_count = geodatabase.get_value_from_db(
        #        dataset=self.dataset,
        #        feature_id=self.feature_id,
        #        field_name="population",
        #    )
        if self.pop_count is None:
            self.pop_count = 0

        query_results = ohsome_client.query(
            layer=self.layer, bpolys=json.dumps(self.bpolys)
        )

        self.feature_count = query_results["result"][0]["value"]
        self.feature_count_per_pop = self.feature_count / self.pop_count
        self.feature_count_per_sqkm = self.feature_count / self.area
        self.pop_count_per_sqkm = self.pop_count / self.area

    def calculate(self):
        # TODO: adjust threshold functions
        # more precise values? maybe as fraction of the threshold functions?
        def greenThresholdFunction(pop_per_sqkm):
            return 5 * np.sqrt(pop_per_sqkm)

        def yellowThresholdFunction(pop_per_sqkm):
            return 0.75 * np.sqrt(pop_per_sqkm)

        logger.info(f"Calculation for indicator: {self.metadata.name}")

        description = Template(self.metadata.result_description).substitute(
            pop_count=self.pop_count,
            area=self.area,
            pop_count_per_sqkm=self.pop_count_per_sqkm,
            feature_count_per_sqkm=self.feature_count_per_sqkm,
        )

        if self.feature_count_per_sqkm <= yellowThresholdFunction(
            self.pop_count_per_sqkm
        ):
            value = (
                self.feature_count_per_sqkm
                / yellowThresholdFunction(self.pop_count_per_sqkm)
            ) * (0.5)
            description += self.metadata.label_description["red"]
            label = TrafficLightQualityLevels.RED

        elif self.feature_count_per_sqkm <= greenThresholdFunction(
            self.pop_count_per_sqkm
        ):
            green = greenThresholdFunction(self.pop_count_per_sqkm)
            yellow = yellowThresholdFunction(self.pop_count_per_sqkm)
            fraction = (self.feature_count_per_sqkm - yellow) / (green - yellow) * 0.5
            value = 0.5 + fraction
            description += self.metadata.label_description["yellow"]
            label = TrafficLightQualityLevels.YELLOW

        else:
            value = 1.0
            description += self.metadata.label_description["green"]
            label = TrafficLightQualityLevels.GREEN

        self.result.label = label
        self.result.value = value
        self.result.description = description

    def create_figure(self):
        def greenThresholdFunction(pop_per_sqkm):
            return 5 * np.sqrt(pop_per_sqkm)

        def yellowThresholdFunction(pop_per_sqkm):
            return 0.75 * np.sqrt(pop_per_sqkm)

        logger.info(f"Create figure for indicator: {self.metadata.name}")

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
        y1 = [greenThresholdFunction(xi) for xi in x]
        y2 = [yellowThresholdFunction(xi) for xi in x]
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

        # Plot point as circle ("o").
        ax.plot(
            self.pop_count_per_sqkm,
            self.feature_count_per_sqkm,
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        logger.info(
            f"Save figure for indicator {self.metadata.name} to: {self.result.svg}"
        )
        plt.savefig(self.result.svg, format="svg")
        plt.close("all")
