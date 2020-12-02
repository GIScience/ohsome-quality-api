import json
from statistics import mean
from typing import Dict, Tuple

import pygal
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Indicator(BaseIndicator):
    """The Last Edit Indicator."""

    name = "LAST_EDIT"
    description = """
        Check the percentage of features that have been edited in the past two years.
    """

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = LEVEL_ONE_LAYERS,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = "2019-07-15,2020-07-15",
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layers=layers,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.time_range = time_range

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        query_results_contributions = ohsome_api.process_ohsome_api(
            endpoint="/contributions/latest/centroid/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
            time=self.time_range,
        )

        query_results_totals = ohsome_api.process_ohsome_api(
            endpoint="/elements/count/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )

        preprocessing_results = {}
        for layer in self.layers.keys():
            edited_features = len(query_results_contributions[layer]["features"])
            total_features = query_results_totals[layer]["result"][0]["value"]

            preprocessing_results[f"{layer}_edited"] = edited_features
            preprocessing_results[f"{layer}_total"] = total_features
            preprocessing_results[f"{layer}_share_edited"] = (
                edited_features / total_features
            )

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")

        text = ""

        # TODO: thresholds might be better defined for each OSM layer
        THRESHOLD_YELLOW = 0.20  # more than 20% edited last year --> green
        THRESHOLD_RED = 0.05  # more than 5% edited last year --> yellow

        levels = []
        result_description_template = (
            "{share}% of the {layer} in OSM have been edited during the last year."
            "This corresponds to a {level} label in regard to data quality.\n\n"
        )

        for layer in self.layers.keys():
            value = preprocessing_results[f"{layer}_share_edited"]

            if value >= THRESHOLD_YELLOW:
                layer_value = TrafficLightQualityLevels.GREEN.value
            elif value >= THRESHOLD_RED:
                layer_value = TrafficLightQualityLevels.YELLOW.value
            else:
                layer_value = TrafficLightQualityLevels.RED.value

            text += result_description_template.format(
                share=round(value * 100, 2),
                layer=layer,
                level=TrafficLightQualityLevels(layer_value).name,
            )
            levels.append(layer_value)

        # get the mean of all labels
        average_level = mean(levels)
        label = TrafficLightQualityLevels(int(round(average_level)))
        value = average_level

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?
        line_chart = pygal.Bar(range=(0, 1))
        line_chart.title = "Features Edited Last Year"

        for layer in self.layers.keys():
            y_data = data[f"{layer}_share_edited"]
            line_chart.add(layer, y_data)

        figure = line_chart.render(is_unicode=True)
        logger.info(f"export figures for {self.name} indicator")
        return figure
