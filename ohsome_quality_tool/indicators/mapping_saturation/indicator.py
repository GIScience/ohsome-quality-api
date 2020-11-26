import json
from datetime import datetime
from typing import Dict

import pygal
from geojson import FeatureCollection
from numpy import diff

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Indicator(BaseIndicator):
    """The Mapping Saturation Indicator."""

    name = "MAPPING_SATURATION"

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = LEVEL_ONE_LAYERS,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = "2008-01-01//P1Y",
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

        query_results = ohsome_api.process_ohsome_api(
            endpoint="elements/{unit}/",
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
            # normalize using maximum value for the time_range
            # for most cases the maximum will be reached at the last timestamp
            normalized_results = [float(i) / max(results) for i in results]
            # e.g. 1 year between data points
            # or usually always same distance between two timestamps,e .g. months
            dx = 1
            slopes_new = diff(normalized_results) / dx

            # calculate slopes between years
            slopes = [0]
            for i in range(1, len(results)):
                if results[i - 1] > 0:
                    slopes.append((results[i] - results[i - 1]) / results[i - 1])

            preprocessing_results["timestamps"] = timestamps
            preprocessing_results[f"{layer}_{unit}"] = results
            preprocessing_results[f"{layer}_{unit}_normalized"] = normalized_results
            preprocessing_results[f"{layer}_{unit}_slopes"] = slopes
            preprocessing_results[f"{layer}_{unit}_slopes_max"] = max(slopes)
            preprocessing_results[f"{layer}_{unit}_slopes_new"] = slopes_new
            preprocessing_results[f"{layer}_{unit}_slopes_new_max"] = max(slopes_new)

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict) -> Dict:
        logger.info(f"run calculation for {self.name} indicator")

        """
        # TODO: find better place to store threshold values
        THRESHOLD_MAJOR_CHANGE = 0.25
        THRESHOLD_YELLOW = 0.05
        THRESHOLD_RED = 0.1

        results = {}
        for cat in preprocessing_results.keys():
            # determine saturation level
            if max(slopes) < THRESHOLD_MAJOR_CHANGE:
                level = 0
                message = (
                    f"Yearly increase of {cat} features never bigger "
                    f"than {int(THRESHOLD_MAJOR_CHANGE*100)}. "
                    f"There might be a lack of data in this area."
                )
            else:
                last_slope = slopes[-1]
                if last_slope > THRESHOLD_RED:
                    level = 0
                    message = (
                        f"The mapping of {cat} features seems to "
                        "be far from a saturated state."
                    )
                elif last_slope > THRESHOLD_YELLOW:
                    level = 1
                    message = (
                        f"The mapping of {cat} features might not be saturated yet."
                    )
                elif last_slope <= THRESHOLD_YELLOW:
                    level = 2
                    message = f"The mapping of {cat} features seems to be saturated."

            results[cat] = {
                "slope_last_year": round(last_slope, 2),
                "saturation_level": level,
                "message": message,
            }
        """

        results = {
            "data": preprocessing_results,
            "quality_level": "tbd",
            "description": "tbd",
        }

        return results

    def create_figure(self, results: Dict):
        # TODO: maybe not all indicators will export figures?
        timestamps = [
            datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
            for x in results["data"]["timestamps"]
        ]
        timestamps_labels = [x.year for x in timestamps]

        line_chart = pygal.Line()
        line_chart.title = "Mapping Saturation"
        line_chart.x_labels = timestamps_labels

        for layer in self.layers.keys():
            unit = self.layers[layer]["unit"]
            data = results["data"][f"{layer}_{unit}_normalized"]
            line_chart.add(layer, data)

        line_chart.render_in_browser()
        figure = line_chart.render_response()
        logger.info(f"export figures for {self.name} indicator")
        return figure
