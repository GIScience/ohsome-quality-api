import io
import json
from math import ceil
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.layers import BUILDING_COUNT_LAYER


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "ghspop-comparison"
    description = """
        The number of features per population count.
        This can give an estimate if mapping has been completed.
    """

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = BUILDING_COUNT_LAYER,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
            layers=layers,
        )

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        if self.dynamic:
            pop_count, area = geodatabase.get_zonal_stats_population(bpolys=self.bpolys)
        else:
            pop_count = geodatabase.get_value_from_db(
                dataset=self.dataset,
                feature_id=self.feature_id,
                field_name="population",
            )
        if pop_count is None:
            pop_count = 0
        # ideally we would have this as a dataframe?
        preprocessing_results = {
            "pop_count": pop_count,
            "area_sqkm": area,
            "pop_count_per_sqkm": pop_count / area,
        }

        query_results = ohsome_api.process_ohsome_api(
            endpoint="elements/{unit}/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )

        for layer in self.layers.keys():
            unit = self.layers[layer]["unit"]
            preprocessing_results[f"{layer}_{unit}"] = query_results[layer]["result"][
                0
            ]["value"]
            preprocessing_results[f"{layer}_{unit}_per_pop"] = (
                preprocessing_results[f"{layer}_{unit}"] / pop_count
            )
            preprocessing_results[f"{layer}_{unit}_per_sqkm"] = (
                preprocessing_results[f"{layer}_{unit}"] / area
            )

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

        if preprocessing_results["buildings_count_per_pop"] <= yellowThresholdFunction(
            preprocessing_results["pop_count_per_sqkm"]
        ):
            value = TrafficLightQualityLevels.RED.value - preprocessing_results[
                "buildings_count_per_pop"
            ] / yellowThresholdFunction(preprocessing_results["pop_count_per_sqkm"])

        elif preprocessing_results["buildings_count_per_pop"] <= greenThresholdFunction(
            preprocessing_results["pop_count_per_sqkm"]
        ):
            green = greenThresholdFunction(preprocessing_results["pop_count_per_sqkm"])
            yellow = yellowThresholdFunction(
                preprocessing_results["pop_count_per_sqkm"]
            )
            fraction = (preprocessing_results["buildings_count_per_pop"] - yellow) / (
                green - yellow
            )
            value = TrafficLightQualityLevels.YELLOW.value - fraction

        else:
            value = TrafficLightQualityLevels.GREEN.value

        label = TrafficLightQualityLevels(ceil(value))

        text = (
            f"{int(preprocessing_results['pop_count'])} of People live in this Area "
            "following the GHS POP Dataset, with a total number of "
            f"{int(preprocessing_results['buildings_count'])} "
            "buildings mapped in OSM. This results in "
            f"{preprocessing_results['buildings_count_per_pop']:.2f} "
            "buildings per person, "
            f"which together with a population density of "
            f"{preprocessing_results['pop_count_per_sqkm']:.2f} "
            "people per sqkm,corresponds to a "
            f"{label.name} "
            "label in regards to Dataquality"
        )

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
            data["buildings_count_per_pop"],
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        # Save as SVG to file-like object and return as string.
        output_file = io.BytesIO()
        plt.savefig(output_file, format="svg")
        logger.info(f"export figures for {self.name} indicator")
        return output_file.getvalue()
