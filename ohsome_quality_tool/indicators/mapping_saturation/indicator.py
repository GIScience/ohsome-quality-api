import json
from typing import Dict, Tuple

import matplotlib.pyplot as plt
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
        y_end_value = results[-1]
        # check if data are there, in case of 0 = no data
        if max_value == 0:
            results_normalized = -1
            results = -1
        # check if data at the end of time period are still there
        elif max_value > 0 and y_end_value == 0:
            results_normalized = -2
            results = -2
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
        if preprocessing_results["results"] == -2:
            # deletion of all data
            text = "Mapping has happened in this region but data " "were deleted. "
            label = TrafficLightQualityLevels.UNDEFINED
            value = -1
            text = text + self.interpretations["undefined"]
            return label, value, text, preprocessing_results
        # prepare the data
        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(preprocessing_results)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)
        # create current data frame
        df1 = pd.DataFrame(
            {
                "timestamps": preprocessing_results["timestamps"],
                "yValues": preprocessing_results["results"],
                "li": li,
            }
        )
        # get y values fot best fitting sigmid curve, with these y the
        # saturation will be calculated
        sigmoid_curve = sigmoidCurve()
        ydataForSat = sigmoid_curve.getBestFittingCurve(preprocessing_results)
        # check if data are more than start stadium
        # The end of the start stage is defined with
        # the maximum of the curvature function f''(x)
        # here: simple check <= 20
        # TODO check for what size (of area or of data) the saturation
        #  makes sense to be calculated
        """
        For buildings-count in a small area, this could return a wrong
        interpretation, eg a little collection of farm house and buildings
        with eg less than 8 buildings, but all buildings are mapped, the value
        would be red, but its all mapped...
        """
        # calculate/define traffic light value and label
        text = ""
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

    def create_figure(self, preprocessing_results: Dict) -> str:
        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(preprocessing_results)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)
        # create current dataframe
        df1 = pd.DataFrame(
            {
                "timestamps": preprocessing_results["timestamps"],
                "yValues": preprocessing_results["results"],
                "li": li,
            }
        )
        # get y values fot best fitting sigmoid curve, with these y the
        # saturation will be calculated
        sigmoid_curve = sigmoidCurve()
        ydataForSat = sigmoid_curve.getBestFittingCurve(preprocessing_results)
        # prepare plot
        # color the lines with different colors
        linecol = ["b-", "g-", "r-", "y-", "black", "gray", "m-", "c-"]
        plt.figure()
        # show nice dates on x axis in plot
        df1["timestamps"] = pd.to_datetime(df1["timestamps"])
        plt.title("Saturation level of the data")
        # plot the data
        plt.plot(
            df1.timestamps,
            df1.yValues,
            linecol[0],
            label=f"{self.layer.name} - {self.layer.unit}",
        )
        # plot sigmoid curve
        plt.plot(df1.timestamps, ydataForSat, linecol[2], label="Sigmoid curve")
        plt.legend()
        plt.savefig(self.outfile, format="svg")
        plt.close("all")
        logger.info(f"saved plot: {self.filename}")
        return self.filename
