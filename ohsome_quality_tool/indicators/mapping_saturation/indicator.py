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
        # initial values for the single sigmoid curve
        initParamsSingle = sigmoid_curve.initparamsingle(df1.li, df1.yValues)
        # initial values for the single sigmoid curve with a different slope
        initParamsSingleB = sigmoid_curve.initparamsingleB(df1.li, df1.yValues)
        # initial values for the sigmoid function with 2 jumps
        initParamsY = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[1]
        L = round(initParamsY[0])
        initParamsX = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[0]
        x1 = round(initParamsX[0])
        x2 = round(initParamsX[1])
        # get initial slopes for the curve with 2 jumps
        ystart2 = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[3]
        k1 = 1 - (ystart2 / initParamsY[0])
        k2 = 1 - (initParamsY[0] / initParamsY[1])
        # get the max y value
        yMax = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[2]
        # --- sigmoid function with 3 and 4 jumps ---
        # get initial y values for the curve with 3 and 4 jumps
        initParamsY3 = sigmoid_curve.sortInits3curves(df1.li, df1.yValues)[1]
        L3 = round(initParamsY3[0])
        L23 = round(initParamsY3[1])
        L34 = round(initParamsY3[2])
        # get initial xmids for the curve with 3 and 4 jumps
        initParamsX3 = sigmoid_curve.sortInits3curves(df1.li, df1.yValues)[0]
        x13 = round(initParamsX3[0])
        x23 = round(initParamsX3[1])
        x33 = round(initParamsX3[2])
        x4 = round(initParamsX3[3])
        # get initial slopes for the curves with 3 and 4 jumps
        ystart3 = sigmoid_curve.sortInits3curves(df1.li, df1.yValues)[3]
        k313 = 1 - (ystart3 / initParamsY3[0])
        k323 = 1 - (initParamsY3[0] / initParamsY3[1])
        k333 = 1 - (initParamsY3[1] / initParamsY3[2])
        k343 = 1 - (initParamsY3[2] / initParamsY3[3])
        # --- sigmoid function with 5 jumps ---
        initParamsY5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[1]
        # get initial y values for the curve with 5 jumps
        L51 = round(initParamsY5[0])
        L52 = round(initParamsY5[1])
        L53 = round(initParamsY5[2])
        L54 = round(initParamsY5[3])
        # get initial xmids for the curve with 5 jumps
        initParamsX5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[0]
        x513 = round(initParamsX5[0])
        x523 = round(initParamsX5[1])
        x533 = round(initParamsX5[2])
        x54 = round(initParamsX5[3])
        x55 = round(initParamsX5[4])
        # get initial slopes for the curve with 5 jumps
        ystart5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[3]
        k13 = 1 - (ystart5 / initParamsY5[0])
        k23 = 1 - (initParamsY5[0] / initParamsY5[1])
        k33 = 1 - (initParamsY5[1] / initParamsY5[2])
        k4 = 1 - (initParamsY5[2] / initParamsY5[3])
        k5 = 1 - (initParamsY5[3] / initParamsY5[4])
        # --- select best fitting curve, with mean_square_error ---
        # get possible xmids
        xmidvalues = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[0]
        errorsListSingle = []
        # check for the xmids the mse error
        for i, xval in enumerate(xmidvalues):
            yPredX = sigmoid_curve.logistic1(
                xval, initParamsSingle[3], initParamsSingle[1], df1.li
            )
            errX = np.sum((yPredX - df1.yValues) ** 2) / len(yPredX)
            errorsListSingle.append(errX)
        # choose the initial x value with min mse
        minX = min(errorsListSingle)
        prefX = xmidvalues[errorsListSingle.index(minX)]
        # mse for logistic1
        # with k as 10.0 / (maxx - minx) from initparamsingle()
        yPredPref = sigmoid_curve.logistic1(
            prefX, initParamsSingle[3], initParamsSingle[1], df1.li
        )
        err1 = np.sum((yPredPref - df1.yValues) ** 2) / len(yPredPref)
        # mse for logistic1 with
        # k as 10.0 / (max(xdata) - min(xdata)) from initparamsingleB()
        yPredB = sigmoid_curve.logistic1(
            prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
        )
        err1B = np.sum((yPredB - df1.yValues) ** 2) / len(yPredB)
        # mse for logistic2
        yPred2 = sigmoid_curve.logistic2(x1, x2, L, yMax, k1, k2, df1.li)
        err2 = np.sum((yPred2 - df1.yValues) ** 2) / len(yPred2)
        # mse for logistic3
        yPred3 = sigmoid_curve.logistic3(
            x13, x23, x33, L3, L23, yMax, k313, k323, k333, df1.li
        )
        err3 = np.sum((yPred3 - df1.yValues) ** 2) / len(yPred3)
        # mse for logistic4
        yPred4 = sigmoid_curve.logistic4(
            x13, x23, x33, x4, L3, L23, L34, yMax, k313, k323, k333, k343, df1.li
        )
        err4 = np.sum((yPred4 - df1.yValues) ** 2) / len(yPred4)
        # mse for logistic5
        yPred5 = sigmoid_curve.logistic5(
            x513,
            x523,
            x533,
            x54,
            x55,
            L51,
            L52,
            L53,
            L54,
            yMax,
            k13,
            k23,
            k33,
            k4,
            k5,
            df1.li,
        )
        err5 = np.sum((yPred5 - df1.yValues) ** 2) / len(yPred5)
        # collect mse in one list
        errorslist = [err1, err1B, err2, err3, err4, err5]
        # collect corresponding function names
        errorslistFuncs = [
            "logistic1",
            "logistic1B",
            "logistic2",
            "logistic3",
            "logistic4",
            "logistic5",
        ]
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
            # depending on best fitted curve calculate ydata with
            # correct function
            if bestfit == "logistic2":
                ydataForSat = sigmoid_curve.logistic2(x1, x2, L, yMax, k1, k2, df1.li)
            elif bestfit == "logistic1":
                ydataForSat = sigmoid_curve.logistic1(
                    prefX, initParamsSingle[3], initParamsSingle[1], df1.li
                )
            elif bestfit == "logistic1B":
                ydataForSat = sigmoid_curve.logistic1(
                    prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
                )
            elif bestfit == "logistic3":
                ydataForSat = sigmoid_curve.logistic3(
                    x13, x23, x33, L3, L23, yMax, k313, k323, k333, df1.li
                )
            elif bestfit == "logistic4":
                ydataForSat = sigmoid_curve.logistic4(
                    x13,
                    x23,
                    x33,
                    x4,
                    L3,
                    L23,
                    L34,
                    yMax,
                    k313,
                    k323,
                    k333,
                    k343,
                    df1.li,
                )
            elif bestfit == "logistic5":
                ydataForSat = sigmoid_curve.logistic5(
                    x513,
                    x523,
                    x533,
                    x54,
                    x55,
                    L51,
                    L52,
                    L53,
                    L54,
                    yMax,
                    k13,
                    k23,
                    k33,
                    k4,
                    k5,
                    df1.li,
                )
            # calculate slope/growth of last 3 years
            # take value in -36. month and value in -1. month of data
            earlyX = li[-36]
            lastX = li[-1]
            # get saturation level within last 3 years
            saturation = sigmoid_curve.getSaturationInLast3Years(
                earlyX, lastX, df1.li, ydataForSat
            )
            # if earlyX and lastX return same y value
            # (means no growth any more),
            # getSaturationInLast3Years returns 1.0
            # if saturation == 1.0:
            #    saturation = 0.0
            logger.info(
                "saturation level last 3 years at: "
                + str(saturation)
                + " that means a growth rate of "
                + str(1 - saturation)
                + " for "
                + f"{self.layer.name} and unit {self.layer.unit}"
            )
        growth = 1 - saturation
        # overall quality
        # 0.0 = saturated
        text = (
            f"Saturation is reached if growth is minimal, "
            f"the value to "
            f"describe completed saturation is 1.0. "
            f"The saturation for the last 3 years is "
            f"{saturation:.3f} "
            f"with a growth rate of {growth:.3f}. "
        )

        # TODO: make clear what should be used here,
        #  if saturation should be used then the threshold
        #  needs to be adjusted
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
        linecol = ["b-", "g-", "r-", "y-", "black", "gray", "m-", "c-"]

        # get API measure type (eg count, length)
        # create current dataframe
        df1 = pd.DataFrame(
            {
                "timestamps": data["timestamps"],
                "yValues": data["results"],
                "li": li,
            }
        )
        # initial values for the single sigmoid curve
        initParamsSingle = sigmoid_curve.initparamsingle(df1.li, df1.yValues)
        # initial values for the single sigmoid curve with a different slope
        initParamsSingleB = sigmoid_curve.initparamsingleB(df1.li, df1.yValues)
        # initial values for the sigmoid function with 2 jumps
        initParamsY = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[1]
        L = round(initParamsY[0])
        initParamsX = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[0]
        x1 = round(initParamsX[0])
        x2 = round(initParamsX[1])
        # get initial slopes for the curve with 2 jumps
        ystart2 = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[3]
        k1 = 1 - (ystart2 / initParamsY[0])
        k2 = 1 - (initParamsY[0] / initParamsY[1])
        # get the max y value
        yMax = sigmoid_curve.sortInits2curves(df1.li, df1.yValues)[2]
        # --- sigmoid function with 3 and 4 jumps ---
        # get initial y values for the curve with 3 and 4 jumps
        initParamsY3 = sigmoid_curve.sortInits3curves(df1.li, df1.yValues)[1]
        L3 = round(initParamsY3[0])
        L23 = round(initParamsY3[1])
        L34 = round(initParamsY3[2])
        # get initial xmids for the curve with 3 and 4 jumps
        initParamsX3 = sigmoid_curve.sortInits3curves(df1.li, df1.yValues)[0]
        x13 = round(initParamsX3[0])
        x23 = round(initParamsX3[1])
        x33 = round(initParamsX3[2])
        x4 = round(initParamsX3[3])
        # get initial slopes for the curves with 3 and 4 jumps
        ystart3 = sigmoid_curve.sortInits3curves(df1.li, df1.yValues)[3]
        k313 = 1 - (ystart3 / initParamsY3[0])
        k323 = 1 - (initParamsY3[0] / initParamsY3[1])
        k333 = 1 - (initParamsY3[1] / initParamsY3[2])
        k343 = 1 - (initParamsY3[2] / initParamsY3[3])
        # --- sigmoid function with 5 jumps ---
        initParamsY5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[1]
        # get initial y values for the curve with 5 jumps
        L51 = round(initParamsY5[0])
        L52 = round(initParamsY5[1])
        L53 = round(initParamsY5[2])
        L54 = round(initParamsY5[3])
        # get initial xmids for the curve with 5 jumps
        initParamsX5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[0]
        x513 = round(initParamsX5[0])
        x523 = round(initParamsX5[1])
        x533 = round(initParamsX5[2])
        x54 = round(initParamsX5[3])
        x55 = round(initParamsX5[4])
        # get initial slopes for the curve with 5 jumps
        ystart5 = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[3]
        k13 = 1 - (ystart5 / initParamsY5[0])
        k23 = 1 - (initParamsY5[0] / initParamsY5[1])
        k33 = 1 - (initParamsY5[1] / initParamsY5[2])
        k4 = 1 - (initParamsY5[2] / initParamsY5[3])
        k5 = 1 - (initParamsY5[3] / initParamsY5[4])
        # --- select best fitting curve, with mean_square_error ---
        # get possible xmids
        xmidvalues = sigmoid_curve.sortInits5curves(df1.li, df1.yValues)[0]
        errorsListSingle = []
        # check for the xmids the mse error
        for i, xval in enumerate(xmidvalues):
            yPredX = sigmoid_curve.logistic1(
                xval, initParamsSingle[3], initParamsSingle[1], df1.li
            )
            errX = np.sum((yPredX - df1.yValues) ** 2) / len(yPredX)
            errorsListSingle.append(errX)
        # choose the initial x value
        # with min mse
        minX = min(errorsListSingle)
        prefX = xmidvalues[errorsListSingle.index(minX)]
        # mse for logistic1 with
        # k as 10.0 / (maxx - minx) from initparamsingle()
        yPredPref = sigmoid_curve.logistic1(
            prefX, initParamsSingle[3], initParamsSingle[1], df1.li
        )
        err1 = np.sum((yPredPref - df1.yValues) ** 2) / len(yPredPref)
        # mse for logistic1 with
        # k as 10.0 / (max(xdata) - min(xdata)) from initparamsingleB()
        yPredB = sigmoid_curve.logistic1(
            prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
        )
        err1B = np.sum((yPredB - df1.yValues) ** 2) / len(yPredB)
        # mse for logistic2
        yPred2 = sigmoid_curve.logistic2(x1, x2, L, yMax, k1, k2, df1.li)
        err2 = np.sum((yPred2 - df1.yValues) ** 2) / len(yPred2)
        # mse for logistic3
        yPred3 = sigmoid_curve.logistic3(
            x13, x23, x33, L3, L23, yMax, k313, k323, k333, df1.li
        )
        err3 = np.sum((yPred3 - df1.yValues) ** 2) / len(yPred3)
        # mse for logistic4
        yPred4 = sigmoid_curve.logistic4(
            x13, x23, x33, x4, L3, L23, L34, yMax, k313, k323, k333, k343, df1.li
        )
        err4 = np.sum((yPred4 - df1.yValues) ** 2) / len(yPred4)
        # mse for logistic5
        yPred5 = sigmoid_curve.logistic5(
            x513,
            x523,
            x533,
            x54,
            x55,
            L51,
            L52,
            L53,
            L54,
            yMax,
            k13,
            k23,
            k33,
            k4,
            k5,
            df1.li,
        )
        err5 = np.sum((yPred5 - df1.yValues) ** 2) / len(yPred5)
        # collect mse in one list
        errorslist = [err1, err1B, err2, err3, err4, err5]
        # collect corresponding function names
        errorslistFuncs = [
            "logistic1",
            "logistic1B",
            "logistic2",
            "logistic3",
            "logistic4",
            "logistic5",
        ]
        # get the smallest mse with its index
        minError = errorslist.index(min(errorslist))
        bestfit = errorslistFuncs[minError]
        # depending on best fitted curve calculate
        # ydata with correct function
        if bestfit == "logistic2":
            ydataForSat = sigmoid_curve.logistic2(x1, x2, L, yMax, k1, k2, df1.li)
        elif bestfit == "logistic1":
            ydataForSat = sigmoid_curve.logistic1(
                prefX, initParamsSingle[3], initParamsSingle[1], df1.li
            )
        elif bestfit == "logistic1B":
            ydataForSat = sigmoid_curve.logistic1(
                prefX, initParamsSingleB[3], initParamsSingleB[1], df1.li
            )
        elif bestfit == "logistic3":
            ydataForSat = sigmoid_curve.logistic3(
                x13, x23, x33, L3, L23, yMax, k313, k323, k333, df1.li
            )
        elif bestfit == "logistic4":
            ydataForSat = sigmoid_curve.logistic4(
                x13, x23, x33, x4, L3, L23, L34, yMax, k313, k323, k333, k343, df1.li
            )
        elif bestfit == "logistic5":
            ydataForSat = sigmoid_curve.logistic5(
                x513,
                x523,
                x533,
                x54,
                x55,
                L51,
                L52,
                L53,
                L54,
                yMax,
                k13,
                k23,
                k33,
                k4,
                k5,
                df1.li,
            )
        # prepare plot
        df1["timestamps"] = pd.to_datetime(df1["timestamps"])
        plt.title("Saturation level of the data")
        plt.plot(
            df1.timestamps,
            df1.yValues,
            linecol[0],
            label=f"{self.layer.name} - {self.layer.unit}",
        )
        plt.plot(df1.timestamps, ydataForSat, linecol[2], label="Sigmoid curve")
        plt.legend()
        plt.savefig(self.outfile, format="svg")
        plt.close("all")
        logger.info(f"saved plot: {self.filename}")
        return self.filename
