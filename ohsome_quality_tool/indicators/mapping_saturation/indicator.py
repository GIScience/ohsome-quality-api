import json
import os
import uuid
from typing import Dict, Tuple

import dateutil.parser
import pygal
from geojson import FeatureCollection
import numpy as np
import pandas as pd

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.indicators.mapping_saturation.sigmoid_curve import sigmoidCurve
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import (
    DATA_PATH,
    TrafficLightQualityLevels,
    logger,
)
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS
from ohsome_quality_tool.utils.label_interpretations import (
    MAPPING_SATURATION_LABEL_INTERPRETATIONS,
)

# threshold values defining the color of the traffic light
# derived directly from MA Katha p24 (mixture of Gröchenig et al. +  Barrington-Leigh)
# 0 < f‘(x) <= 0.03 and years with saturation > 2
THRESHOLD_YELLOW = 0.03
THRESHOLD_RED = 10

class Indicator(BaseIndicator):
    """The Mapping Saturation Indicator."""

    name = "MAPPING_SATURATION"
    description = """
        Calculate if mapping has saturated.
    """
    interpretations: Dict = MAPPING_SATURATION_LABEL_INTERPRETATIONS

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

        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(preprocessing_results)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)

        # dict to collect saturation values of each layer for individual layer traffic light
        satValCollection = {}
        # list for collecting saturation values of each layer
        overallSaturation = []

        for layer in self.layers.keys():
            # calculate traffic light value for each layer
            unit = self.layers[layer]["unit"]

            #pass
            df1 = pd.DataFrame(
                {'timestamps': preprocessing_results["timestamps"],
                 'yValues': preprocessing_results[f"{layer}_{unit}"],
                 'li': li
                 })

            # get init params for sigmoid curve with 2 jumps
            sigmoid_curve = sigmoidCurve()

            initParams = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[0]

            x1 = round(initParams[0])
            x2 = round(initParams[2])
            L = round(initParams[1])
            L2 = round(initParams[3])

            # get initial slopes for the 2 curves
            inits = sigmoid_curve.initparamsFor2JumpsCurve(df1.li, df1.yValues)
            yY = sigmoid_curve.getFirstLastY(inits)
            k1 = yY[0] / yY[1]
            k2 = yY[1] / yY[2]

            # TODO select best fitting curve, eg with mean_square_error

            # check if data are more than start stadium
            # The end of the start stage is defined with the maximum of the curvature function f''(x)
            # here: simple check
            if  (max(df1.yValues) <= 20):
                # start stadium
                label = TrafficLightQualityLevels.RED
                value = 0.25
                text = text + self.interpretations["red"]
            else:
                # if so
                # calculate slope/growth of last 3 years
                # take value in -36 month before end time and value in last month of data
                earlyX = li[-36]
                lastX = li[-1]
                ydata = sigmoid_curve.logistic2(x1, x2, L, L2, k1, k2, df1.li)
                saturation = sigmoid_curve.getSaturationInLast3Years(earlyX, lastX, df1.li, ydata)
                logger.info("satruation level last 3 years at: " + str(saturation) + " for " + f"{layer}_{unit}")
                # perhaps needed for individual layer descirption/traffic light?
                satValCollection[f"{layer}_{unit}" ] = saturation
                overallSaturation.append(saturation)

        # overall quality
        result = sum(overallSaturation)/len(overallSaturation)
        text = (
            f"The saturation for the last 3 years is {result}."
        )

        if result <= THRESHOLD_YELLOW:
            label = TrafficLightQualityLevels.GREEN
            value = 0.75
            text = text + self.interpretations["green"]
        else:
            # THRESHOLD_YELLOW > result > THRESHOLD_RED
            label = TrafficLightQualityLevels.YELLOW
            value = 0.5
            text = text + self.interpretations["yellow"]

        logger.info(
            f"result density value: {result}, label: {label},"
            f" value: {value}, text: {text}"
        )

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

        if self.dynamic:
            # generate a random ID for the outfile name
            random_id = uuid.uuid1()
            filename = f"{self.name}_{random_id}.svg"
            outfile = os.path.join(DATA_PATH, filename)
        else:
            filename = f"{self.name}_{self.dataset}_{self.feature_id}.svg"
            outfile = os.path.join(DATA_PATH, filename)

        line_chart.render_to_file(outfile)
        logger.info(f"exported figure: {outfile}")
        return filename
