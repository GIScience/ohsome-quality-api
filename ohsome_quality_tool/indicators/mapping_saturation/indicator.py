import json
from string import Template
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.indicators.mapping_saturation.sigmoid_curve import sigmoidCurve
from ohsome_quality_tool.ohsome import client as ohsome_client
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger

# threshold values defining the color of the traffic light
# derived directly from MA Katha p24 (mixture of Gröchenig et al. +  Barrington-Leigh)
# 0 < f‘(x) <= 0.03 and years with saturation > 2
THRESHOLD_YELLOW = 0.03
THRESHOLD_RED = 10


class MappingSaturation(BaseIndicator):
    """The Mapping Saturation Indicator."""

    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = "2008-01-01//P1M",
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.time_range = time_range
        # Those attributes will be set during lifecycle of the object.
        self.saturation = None
        self.growth = None
        self.preprocessing_results = None

    def preprocess(self) -> Dict:
        """Get data from ohsome API and db. Put timestamps + data in list"""

        logger.info(f"Preprocessing for indicator: {self.metadata.name}")

        query_results = ohsome_client.query(
            layer=self.layer, bpolys=json.dumps(self.bpolys), time=self.time_range
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

        self.preprocessing_results = {
            "timestamps": timestamps,
            "results": results,
            "results_normalized": results_normalized,
        }

    def calculate(self):

        logger.info(f"run calculation for : {self.metadata.name}")

        description = Template(self.metadata.result_description).substitute(
            saturation=self.saturation, growth=self.growth
        )
        # check if any mapping happened in this region
        # and directly return quality label if no mapping happened
        if self.preprocessing_results["results"] == -1:
            # start stadium
            text = "No mapping has happened in this region. "
            label = TrafficLightQualityLevels.UNDEFINED
            value = -1
            description += self.metadata.label_description["undefined"]
            self.result.label = label
            self.result.value = value
            self.result.description = description
            return label, value, text, self.preprocessing_results
        if self.preprocessing_results["results"] == -2:
            # deletion of all data
            text = "Mapping has happened in this region but data " "were deleted. "
            label = TrafficLightQualityLevels.UNDEFINED
            value = -1
            description += self.metadata.label_description["undefined"]
            self.result.label = label
            self.result.value = value
            self.result.description = description
            return label, value, text, self.preprocessing_results
        # prepare the data
        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(self.preprocessing_results)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)
        # create current data frame
        df1 = pd.DataFrame(
            {
                "timestamps": self.preprocessing_results["timestamps"],
                "yValues": self.preprocessing_results["results"],
                "li": li,
            }
        )
        # get y values fot best fitting sigmid curve, with these y the
        # saturation will be calculated
        sigmoid_curve = sigmoidCurve()
        ydataForSat = sigmoid_curve.getBestFittingCurve(self.preprocessing_results)
        if ydataForSat[0] != "empty":
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
            if max(df1.yValues) <= 20:
                # start stadium
                label = TrafficLightQualityLevels.RED
                value = 0.0
                description += self.metadata.label_description["red"]
            else:
                # calculate slope/growth of last 3 years
                # take value in -36. month and value in -1. month of data
                earlyX = li[-36]
                lastX = li[-1]
                # get saturation level within last 3 years
                self.saturation = sigmoid_curve.getSaturationInLast3Years(
                    earlyX, lastX, df1.li, ydataForSat
                )
                # if earlyX and lastX return same y value
                # (means no growth any more),
                # getSaturationInLast3Years returns 1.0
                # if saturation == 1.0:
                #    saturation = 0.0

            self.growth = 1 - self.saturation

            # TODO: make clear what should be used here,
            #  if saturation should be used then the threshold
            #  needs to be adjusted
            if self.growth <= THRESHOLD_YELLOW:
                label = TrafficLightQualityLevels.GREEN
                value = 1.0
                description += self.metadata.label_description["green"]
            else:
                # THRESHOLD_YELLOW > saturation > THRESHOLD_RED
                label = TrafficLightQualityLevels.YELLOW
                value = 0.5
                description += self.metadata.label_description["yellow"]

            description = Template(self.metadata.result_description).substitute(
                saturation=self.saturation, growth=self.growth
            )
            self.result.label = label
            self.result.value = value
            self.result.description = description
            logger.info(
                f"result saturation value: {self.saturation}, label: {label},"
                f" value: {value}, description: {description}"
            )
        else:
            # deletion of all data
            text = "Mapping has happened in this region but data " "were deleted. "
            label = TrafficLightQualityLevels.UNDEFINED
            value = -1
            description += self.metadata.label_description["undefined"]
            self.result.label = label
            self.result.value = value
            self.result.description = description
            return label, value, text, self.preprocessing_results

    def create_figure(self) -> str:
        # not nice work around to avoid error ".. is not indexable"
        dfWorkarkound = pd.DataFrame(self.preprocessing_results)
        li = []
        for i in range(len(dfWorkarkound)):
            li.append(i)
        # create current dataframe
        df1 = pd.DataFrame(
            {
                "timestamps": self.preprocessing_results["timestamps"],
                "yValues": self.preprocessing_results["results"],
                "li": li,
            }
        )
        # get y values fot best fitting sigmoid curve, with these y the
        # saturation will be calculated
        sigmoid_curve = sigmoidCurve()
        ydataForSat = sigmoid_curve.getBestFittingCurve(self.preprocessing_results)
        # prepare plot
        # color the lines with different colors
        linecol = ["b-", "g-", "r-", "y-", "black", "gray", "m-", "c-"]
        plt.figure()
        # show nice dates on x axis in plot
        df1["timestamps"] = pd.to_datetime(df1["timestamps"])
        # plot the data
        plt.plot(
            df1.timestamps,
            df1.yValues,
            linecol[0],
            label=f"{self.layer.name} - {self.layer.endpoint}",
        )
        if ydataForSat[0] != "empty":
            plt.title("Saturation level of the data")
            # plot sigmoid curve
            plt.plot(df1.timestamps, ydataForSat, linecol[2], label="Sigmoid curve")
        else:
            plt.title("No Sigmoid curve could be fitted into the data")
        plt.legend()
        plt.savefig(self.result.svg, format="svg")
        plt.close("all")
        logger.info(
            f"Save figure for indicator {self.metadata.name} to: {self.result.svg}"
        )
