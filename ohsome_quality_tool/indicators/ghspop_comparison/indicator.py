import json
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.label_interpretations import (
    GHSPOP_COMPARISON_LABEL_INTERPRETATIONS,
)


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "ghspop-comparison"
    description = """
        Comparison between population density and feature density.
        This can give an estimate if mapping has been completed.
    """

    def __init__(
        self,
        dynamic: bool,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
            layer_name=layer_name,
        )

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        # if self.dynamic:
        pop_count, area = geodatabase.get_zonal_stats_population(bpolys=self.bpolys)
        # else:
        #    pop_count = geodatabase.get_value_from_db(
        #        dataset=self.dataset,
        #        feature_id=self.feature_id,
        #        field_name="population",
        #    )
        if pop_count is None:
            pop_count = 0

        query_results = ohsome_api.query_ohsome_api(
            endpoint="elements/count/",
            filter_string=self.layer.filter,
            bpolys=json.dumps(self.bpolys),
        )

        count = query_results["result"][0]["value"]
        count_per_pop = count / pop_count
        count_per_sqkm = count / area

        # ideally we would have this as a dataframe?
        preprocessing_results = {
            "pop_count": pop_count,
            "area_sqkm": area,
            "pop_count_per_sqkm": pop_count / area,
            "feature_count": count,
            "feature_count_per_pop": count_per_pop,
            "feature_count_per_sqkm": count_per_sqkm,
        }

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")
        # TODO: adjust threshold functions
        # more precise values? maybe as fraction of the threshold functions?

        def greenThresholdFunction(pop_per_sqkm):
            return 5 * np.sqrt(pop_per_sqkm)

        def yellowThresholdFunction(pop_per_sqkm):
            return 0.75 * np.sqrt(pop_per_sqkm)

        text = (
            "Following the GHS POP dataset, there are"
            f"{int(preprocessing_results['pop_count'])} People living,"
            f" in an area of { preprocessing_results['area_sqkm']:.2f} sqkm, "
            "which results in a Population density "
            f"{ preprocessing_results['pop_count_per_sqkm']:.2f} of People per sqkm. "
            f"In OSM there are { preprocessing_results['feature_count_per_sqkm']}"
            " Buildings per sqkm mapped."
        )

        if preprocessing_results["feature_count_per_sqkm"] <= yellowThresholdFunction(
            preprocessing_results["pop_count_per_sqkm"]
        ):
            value = (
                preprocessing_results["feature_count_per_sqkm"]
                / yellowThresholdFunction(preprocessing_results["pop_count_per_sqkm"])
            ) * (0.5)
            text += GHSPOP_COMPARISON_LABEL_INTERPRETATIONS["red"]
            label = TrafficLightQualityLevels.RED

        elif preprocessing_results["feature_count_per_sqkm"] <= greenThresholdFunction(
            preprocessing_results["pop_count_per_sqkm"]
        ):
            green = greenThresholdFunction(preprocessing_results["pop_count_per_sqkm"])
            yellow = yellowThresholdFunction(
                preprocessing_results["pop_count_per_sqkm"]
            )
            fraction = (
                (preprocessing_results["feature_count_per_sqkm"] - yellow)
                / (green - yellow)
                * 0.5
            )
            value = 0.5 + fraction
            text += GHSPOP_COMPARISON_LABEL_INTERPRETATIONS["yellow"]
            label = TrafficLightQualityLevels.YELLOW

        else:
            value = 1.0
            text += GHSPOP_COMPARISON_LABEL_INTERPRETATIONS["green"]
            label = TrafficLightQualityLevels.GREEN

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        def greenThresholdFunction(pop_per_sqkm):
            return 5 * np.sqrt(pop_per_sqkm)

        def yellowThresholdFunction(pop_per_sqkm):
            return 0.75 * np.sqrt(pop_per_sqkm)

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Buildings per person against people per $km^2$")
        ax.set_xlabel("Population Density [$1/km^2$]")
        ax.set_ylabel("Building Density [$1/km^2$]")

        # Set x max value based on area
        if data["pop_count_per_sqkm"] < 100:
            max_area = 10
        else:
            max_area = round(data["pop_count_per_sqkm"] * 2 / 10) * 10
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
        ax.fill_between(x, y1, max(y1), alpha=0.5, color="green")

        # Plot point as circle ("o").
        ax.plot(
            data["pop_count_per_sqkm"],
            data["feature_count_per_sqkm"],
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        plt.savefig(self.outfile, format="svg")
        plt.close("all")
        logger.info(f"saved plot: {self.filename}")
        return self.filename
