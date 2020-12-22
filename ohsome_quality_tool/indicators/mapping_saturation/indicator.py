import json
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.indicators.mapping_saturation.sigmoid_curve import sigmoidCurve
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
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

    name = "mapping-saturation"
    description = """
        Calculate if mapping has saturated.
    """
    interpretations: Dict = MAPPING_SATURATION_LABEL_INTERPRETATIONS

    def __init__(
        self,
        dynamic: bool,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = "2008-01-01//P1M",
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layer_name=layer_name,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.time_range = time_range

    def preprocess(self) -> Dict:
        """Get data from ohsome API and db. Put timestamps + data in list"""

        logger.info(f"run preprocessing for {self.name} indicator")

        query_results = ohsome_api.query_ohsome_api(
            endpoint=f"elements/{self.layer.unit}/",  # unit is defined in layers.py
            filter_string=self.layer.filter,
            bpolys=json.dumps(self.bpolys),
            time=self.time_range,
        )

        results = [y_dict["value"] for y_dict in query_results["result"]]
        timestamps = [y_dict["timestamp"] for y_dict in query_results["result"]]
        max_value = max(results)

        if max_value == 0:
            results_normalized = -1
            results = -1
        else:
            results_normalized = [result / max_value for result in results]

        preprocessing_results = {
            "timestamps": timestamps,
            "results": results,
            "results_normalized": results_normalized,
        }

        return preprocessing_results

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:

        logger.info(f"run calculation for {self.name} indicator")

        # check if any mapping happened in this region
        # and directly return quality label if no mapping happened
        if preprocessing_results["results"] == -1:
            # start stadium
            text = "No mapping has happened in this region. "
            label = TrafficLightQualityLevels.UNDEFINED
            value = -1
            text = text + self.interpretations["undefined"]
            return label, value, text, preprocessing_results

        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(preprocessing_results)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)

        text = ""

        # calculate traffic light value
        df1 = pd.DataFrame(
            {
                "timestamps": preprocessing_results["timestamps"],
                "yValues": preprocessing_results["results"],
                "li": li,
            }
        )

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

        # select best fitting curve, with mean_square_error
        # mse for logistic1 with k as 10.0 / (maxx - minx) from initparamsingle()
        initParamsSingle = sigmoid_curve.initparamsingle(df1.li, df1.yValues)
        yPred = sigmoid_curve.logistic1(
            initParamsSingle[4], initParamsSingle[3], initParamsSingle[1], df1.li
        )
        err1a = np.sum((yPred - df1.yValues) ** 2) / len(yPred)

        # mse for logistic1 with k as 10.0 / (max(xdata) - min(xdata))
        # from initparamsingleB()
        initParamsSingleB = sigmoid_curve.initparamsingleB(df1.li, df1.yValues)
        yPredB = sigmoid_curve.logistic1(
            initParamsSingleB[4], initParamsSingleB[3], initParamsSingleB[1], df1.li
        )
        err1B = np.sum((yPredB - df1.yValues) ** 2) / len(yPredB)

        # mse for logistic2
        yPred2 = sigmoid_curve.logistic2(x1, x2, L, L2, k1, k2, df1.li)
        err2 = np.sum((yPred2 - df1.yValues) ** 2) / len(yPred2)

        # collect mse in one list
        errorslist = [err1a, err1B, err2]
        # collect corresponding function names
        errorslistFuncs = ["logistic1", "logistic1B", "logistic2"]
        # get the smallest mse with its index
        minError = errorslist.index(min(errorslist))
        bestfit = errorslistFuncs[minError]

        # check if data are more than start stadium
        # The end of the start stage is defined with
        # the maximum of the curvature function f''(x)
        # here: simple check <= 20
        if max(df1.yValues) <= 20:
            # start stadium
            label = TrafficLightQualityLevels.RED
            value = 0.0
            text = text + self.interpretations["red"]
        else:
            # calculate slope/growth of last 3 years
            # take value in -36. month and value in -1. month of data
            earlyX = li[-36]
            lastX = li[-1]
            # depending on best fitted curve calculate ydata with correct function
            if bestfit == "logistic2":
                ydataForSat = sigmoid_curve.logistic2(x1, x2, L, L2, k1, k2, df1.li)
            elif bestfit == "logistic1":
                ydataForSat = sigmoid_curve.logistic1(
                    initParamsSingle[4],
                    initParamsSingle[3],
                    initParamsSingle[1],
                    df1.li,
                )
            elif bestfit == "logistic1B":
                ydataForSat = sigmoid_curve.logistic1(
                    initParamsSingleB[4],
                    initParamsSingleB[3],
                    initParamsSingleB[1],
                    df1.li,
                )
            # get saturation level within last 3 years
            saturation = sigmoid_curve.getSaturationInLast3Years(
                earlyX, lastX, df1.li, ydataForSat
            )
            # if earlyX and lastX return same y value (means no growth any more),
            # getSaturationInLast3Years returns 1.0
            if saturation == 1.0:
                saturation = 0.0
            logger.info(
                "saturation level last 3 years at: "
                + str(saturation)
                + " for "
                + f"{self.layer.name} and unit {self.layer.unit}"
            )

        # overall quality
        # 0.0 = saturated
        text = f"The saturation for the last 3 years is {saturation:.1f}. "

        # TODO: make clear what should be used here,
        #   if saturation should be used then the threshold needs to be adjusted
        growth = 1 - saturation
        if growth <= THRESHOLD_YELLOW:
            label = TrafficLightQualityLevels.GREEN
            value = 1.0
            text = text + self.interpretations["green"]
        else:
            # THRESHOLD_YELLOW > saturation > THRESHOLD_RED
            label = TrafficLightQualityLevels.YELLOW
            value = 0.5
            text = text + self.interpretations["yellow"]

        logger.info(
            f"result saturation value: {saturation}, label: {label},"
            f" value: {value}, text: {text}"
        )

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?
        # TODO: onevsg per layer?

        # get init params for sigmoid curve with 2 jumps
        sigmoid_curve = sigmoidCurve()
        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(data)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)

        plt.figure()
        # color the lines with different colors
        # TODO: what if more than 5 layers are in there?
        linecol = ["b-", "g-", "r-", "y-", "black-"]

        # get API measure type (eg count, length)
        # create current dataframe
        df1 = pd.DataFrame(
            {
                "timestamps": data["timestamps"],
                "yValues": data["results"],
                "li": li,
            }
        )
        # initial values for the sigmoid function
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

        # select best fitting curve, with mean_square_error
        # mse for logistic1 with k as 10.0 / (maxx - minx) from initparamsingle()
        initParamsSingle = sigmoid_curve.initparamsingle(df1.li, df1.yValues)
        ydataSingle = sigmoid_curve.logistic1(
            initParamsSingle[4], initParamsSingle[3], initParamsSingle[1], df1.li
        )
        yPred = sigmoid_curve.logistic1(
            initParamsSingle[4], initParamsSingle[3], initParamsSingle[1], df1.li
        )
        err1a = np.sum((yPred - df1.yValues) ** 2) / len(yPred)
        # mse for logistic1 with k as 10.0 / (max(xdata) - min(xdata)) from
        # initparamsingleB()
        initParamsSingleB = sigmoid_curve.initparamsingleB(df1.li, df1.yValues)
        ydataSingleB = sigmoid_curve.logistic1(
            initParamsSingleB[4], initParamsSingleB[3], initParamsSingleB[1], df1.li
        )
        yPredB = sigmoid_curve.logistic1(
            initParamsSingleB[4], initParamsSingleB[3], initParamsSingleB[1], df1.li
        )
        err1B = np.sum((yPredB - df1.yValues) ** 2) / len(yPredB)
        # mse for logistic2
        yPred2 = sigmoid_curve.logistic2(x1, x2, L, L2, k1, k2, df1.li)
        err2 = np.sum((yPred2 - df1.yValues) ** 2) / len(yPred2)
        # collect mse in one list
        errorslist = [err1a, err1B, err2]
        # collect corresponding function names
        errorslistFuncs = ["logistic1", "logistic1B", "logistic2"]
        # get the smallest mse with its index
        minError = errorslist.index(min(errorslist))
        bestfit = errorslistFuncs[minError]
        # prepare plot
        plt.title("Data with sigmoid curve, best fit: " + bestfit)
        plt.plot(
            df1.li,
            df1.yValues,
            linecol[0],
            label=f"{self.layer.name} - {self.layer.unit}",
        )
        plt.plot(df1.li, yPred2, linecol[2], label="Sigmoid curve with 2 jumps")
        plt.plot(df1.li, ydataSingle, linecol[3], label="logistic1")
        plt.plot(df1.li, ydataSingleB, linecol[1], label="logistic1 B")
        plt.legend()
        plt.savefig(self.outfile, format="svg")
        plt.close("all")
        logger.info(f"saved plot: {self.filename}")
        return self.filename
