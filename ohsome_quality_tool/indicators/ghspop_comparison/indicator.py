import json
from typing import Dict, Tuple

import numpy as np
import pygal
from geojson import FeatureCollection
from pygal.style import Style

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "GHSPOP_COMPARISON"
    description = """
        The number of features per population count.
        This can give an estimate if mapping has been completed.
    """

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = {
            "buildings": {
                "description": """
            All buildings as defined by all objects tagged with 'building=*'.
        """,
                "filter": "building=*",
                "unit": "count",
            }
        },
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

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")
        # TODO: adjust threshold functions
        # more precise values? maybe as fraction of the threshold functions?

        def greenThresholdFunction(pop_per_sqkm):
            return 0.03 - (0.03 - 0.3) * np.exp(-0.0004 * pop_per_sqkm)

        def yellowThresholdFunction(pop_per_sqkm):
            return 1.5 * (10.0 ** (-2)) - (1.5 * (10.0 ** (-2)) - 0.1) * np.exp(
                -0.0005 * pop_per_sqkm
            )

        """greenThresholdFunction = lambda pop_per_sqkm: 0.05 - (0.05 - 0.3) * np.exp(
            -0.0002 * pop_per_sqkm
        )
        yellowThresholdFunction = lambda pop_per_sqkm: 10.0 ** (-2)*- (
            10.0 ** (-2) - 0.04
        ) * np.exp(-0.0003 * pop_per_sqkm)"""

        if preprocessing_results["buildings_count_per_pop"] <= yellowThresholdFunction(
            preprocessing_results["pop_count_per_sqkm"]
        ):
            value = TrafficLightQualityLevels.RED.value
        elif preprocessing_results["buildings_count_per_pop"] <= greenThresholdFunction(
            preprocessing_results["pop_count_per_sqkm"]
        ):
            value = TrafficLightQualityLevels.YELLOW.value
        else:
            value = TrafficLightQualityLevels.GREEN.value

        label = TrafficLightQualityLevels(value)

        text = (
            f"{preprocessing_results['pop_count']:.2f} of People live in this Area "
            "following the GHS POP Dataset, with a total number "
            f"{preprocessing_results['buildings_count']}"
            "buildings mapped in OSM. This results in "
            f"{preprocessing_results['buildings_count_per_pop']:.2f}"
            "buildings per person, "
            f"which together with a population density of "
            f"{preprocessing_results['pop_count_per_sqkm']:.2f}"
            "people per sqkm,corresponds to a "
            f"{label.name}"
            "label in regards to Dataquality"
        )

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # is it possible to comibine diffrent pygal chart types ie stacked and xy?
        CustomStyle = Style(colors=("green", "yellow", "blue"))
        xy_chart = pygal.XY(stroke=True, style=CustomStyle)
        x = np.linspace(0, 40000, 40)

        def greenThresholdFunction(pop_per_sqkm):
            return 0.03 - (0.03 - 0.3) * np.exp(-0.0004 * pop_per_sqkm)

        def yellowThresholdFunction(pop_per_sqkm):
            return 1.5 * (10.0 ** (-2)) - (1.5 * (10.0 ** (-2)) - 0.1) * np.exp(
                -0.0005 * pop_per_sqkm
            )

        xy_chart.add(
            " Green threshold ", [(xi, greenThresholdFunction(xi)) for xi in x]
        )
        xy_chart.add(
            " Yellow threshold ", [(xi, yellowThresholdFunction(xi)) for xi in x]
        )
        xy_chart.add(
            "location", [(data["pop_count_per_sqkm"], data["buildings_count_per_pop"])]
        )
        xy_chart.title = "Buildings per person against people per sqkm"
        figure = xy_chart.render(is_unicode=True)
        logger.info(f"export figures for {self.name} indicator")
        return figure
