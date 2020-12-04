import json
import statistics
from datetime import datetime
from typing import Dict, Tuple

import pygal
from geojson import FeatureCollection
from numpy import diff

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
            if max(results) > 0:
                normalized_results = [float(i) / max(results) for i in results]
            else:
                normalized_results = [0] * len(results)
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

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        logger.info(f"run calculation for {self.name} indicator")

        INCREASING_TREND_THRESHOLD = 0.02
        DECREASING_TREND_THRESHOLD = -0.02
        ONE_TIME_MAPPING_THRESHOLD = 0.5
        NO_MAPPING_ACTIVITY_THRESHOLD = 0.005

        quality_levels = []
        for layer in self.layers.keys():
            # check slope for last year
            unit = self.layers[layer]["unit"]
            slopes = preprocessing_results[f"{layer}_{unit}_slopes_new"]
            if slopes[-1] >= INCREASING_TREND_THRESHOLD:
                trend = "increasing"
            elif slopes[-1] <= DECREASING_TREND_THRESHOLD:
                trend = "decreasing"
            else:
                trend = "no_trend"

            # check for one time mapping activity
            # TODO: maybe this would be an indicator for itself?
            one_time_mapping = False
            one_time_mapping_times = []
            one_time_mapping_slopes = []
            for j, slope in enumerate(slopes):
                if slope >= ONE_TIME_MAPPING_THRESHOLD:
                    one_time_mapping = True
                    timestamp = preprocessing_results["timestamps"][j]
                    one_time_mapping_times.append(timestamp)
                    one_time_mapping_slopes.append(slope)

            # check for times without mapping activity
            no_mapping = False
            no_mapping_times = []
            no_mapping_slopes = []
            for k, slope in enumerate(slopes[::-1]):  # reversed slopes array
                if abs(slope) <= NO_MAPPING_ACTIVITY_THRESHOLD:
                    timestamp = preprocessing_results["timestamps"][::-1][k]
                    no_mapping_times.append(timestamp)
                    no_mapping_slopes.append(slope)
                    no_mapping = True
                else:
                    break

            # quality classification
            QUALITY_LEVEL_GREEN_CONDITION = (
                (trend == "no_trend" or trend == "decreasing")
                and (one_time_mapping is False or max(one_time_mapping_times) < "2015")
                and (no_mapping is False or len(no_mapping_times) < 3)
            )

            QUALITY_LEVEL_YELLOW_CONDITION = (
                (trend == "increasing")
                or (one_time_mapping is True)
                or (len(no_mapping_times) >= 3)
            )

            if QUALITY_LEVEL_GREEN_CONDITION:
                quality_level = TrafficLightQualityLevels.GREEN
            elif QUALITY_LEVEL_YELLOW_CONDITION:
                quality_level = TrafficLightQualityLevels.YELLOW
            else:
                quality_level = TrafficLightQualityLevels.RED

            quality_results = {
                "quality_level": quality_level,
                "trend": trend,
                "no_mapping": no_mapping,
                "no_mapping_times": no_mapping_times,
                "one_time_mapping": one_time_mapping,
                "one_time_mapping_times": one_time_mapping_times,
                "one_time_mapping_slopes": one_time_mapping_slopes,
            }
            quality_levels.append(quality_level.value)
            print(quality_results)

        # get average quality level
        overall_quality_level = int(round(statistics.mean(quality_levels)))
        overall_quality_level = TrafficLightQualityLevels(overall_quality_level)
        print(overall_quality_level)

        # each indicator need to provide these
        label = TrafficLightQualityLevels.YELLOW
        value = 0.5
        text = "test test test"

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?
        timestamps = [
            datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ") for x in data["timestamps"]
        ]
        timestamps_labels = [x.year for x in timestamps]

        line_chart = pygal.Line()
        line_chart.title = "Mapping Saturation"
        line_chart.x_labels = timestamps_labels

        for layer in self.layers.keys():
            unit = self.layers[layer]["unit"]
            y_data = data[f"{layer}_{unit}_normalized"]
            line_chart.add(layer, y_data)

        figure = line_chart.render(is_unicode=True)
        logger.info(f"export figures for {self.name} indicator")
        return figure
