import json
from typing import Dict, Tuple

import dateutil.parser
import pygal
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Indicator(BaseIndicator):
    """The Mapping Saturation Indicator."""

    name = "MAPPING_SATURATION"
    description = """
        Calculate if mapping has saturated.
    """

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = LEVEL_ONE_LAYERS,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = "2008-01-01//P1M",
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
        """Get data from ohsome API and db. Put timestamps + data in list"""

        logger.info(f"run preprocessing for {self.name} indicator")

        query_results = ohsome_api.process_ohsome_api(
            endpoint="elements/{unit}/",  # unit is defined in layers.py
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
            time=self.time_range,
        )

        preprocessing_results = {}

        for layer in self.layers.keys():
            unit = self.layers[layer]["unit"]
            results = [y_dict["value"] for y_dict in query_results[layer]["result"]]
            timestamps = [
                y_dict["timestamp"] for y_dict in query_results[layer]["result"]
            ]
            max_value = max(results)

            preprocessing_results["timestamps"] = timestamps
            preprocessing_results[f"{layer}_{unit}"] = results
            preprocessing_results[f"{layer}_{unit}_normalized"] = [
                result / max_value for result in results
            ]

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:

        logger.info(f"run calculation for {self.name} indicator")

        for layer in self.layers.keys():
            # calculate traffic light value for each layer
            pass

        # 4 values, calculate average value out of it

        # overall quality (placeholder)
        label = TrafficLightQualityLevels.YELLOW
        value = 0.5  # = average value
        text = "test test test"

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?

        line_chart = pygal.XY()

        # a complicated way to add labels
        timestamps = data["timestamps"]
        x_labels = []
        for k, t in enumerate(timestamps):
            timestamp = dateutil.parser.parse(t)
            year = timestamp.year
            month = timestamp.month
            if month == 1:
                x_labels.append({"value": k, "label": str(year)})

        # add plot for each layer
        for i, layer in enumerate(self.layers.keys()):
            unit = self.layers[layer]["unit"]
            query_results = data[f"{layer}_{unit}"]
            max_value = max(query_results)

            # use normalized values to be able to compare different features,
            # e.g. buildings and highways
            results_norm = [
                (h, result / max_value) for h, result in enumerate(query_results)
            ]

            line_chart.add(layer, results_norm)

        line_chart.x_labels = x_labels
        figure = line_chart.render(is_unicode=True)

        return figure
