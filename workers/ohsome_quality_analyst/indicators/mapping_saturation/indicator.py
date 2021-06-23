import logging
from io import StringIO
from string import Template
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd
from geojson import MultiPolygon, Polygon

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.indicators.mapping_saturation.sigmoid_curve import (
    sigmoidCurve,
)
from ohsome_quality_analyst.ohsome import client as ohsome_client

# threshold values defining the color of the traffic light
# derived directly from MA Katha p24 (mixture of Gröchenig et al. +  Barrington-Leigh)
# saturation: 0 < f‘(x) <= 0.03 and years with saturation > 2
THRESHOLD_YELLOW = 0.03
# TODO define THRESHOLD_RED (where start stadium ends) with function from MA


class MappingSaturation(BaseIndicator):
    """The Mapping Saturation Indicator."""

    def __init__(
        self,
        layer_name: str,
        bpolys: Union[Polygon, MultiPolygon] = None,
        time_range: str = "2008-01-01//P1M",
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            bpolys=bpolys,
        )
        self.time_range = time_range
        # Those attributes will be set during lifecycle of the object.
        self.saturation = None
        self.growth = None
        self.preprocessing_results = None

    async def preprocess(self) -> bool:
        """Get data from ohsome API and db. Put timestamps + data in list"""
        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=self.bpolys, time=self.time_range
        )
        if query_results is None:
            return False
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
        return True

    def calculate(self) -> bool:
        """
        Calculate the growth rate + saturation level within the last 3 years.
        Depending on the result, define label and value.
        """
        description = ""
        # check if any mapping happened in this region
        # and directly return quality label if no mapping happened
        if self.preprocessing_results["results"] == -1:
            # start stadium
            # "No mapping has happened in this region. "
            label = "undefined"
            value = None
            description += self.metadata.label_description["undefined"]
            self.result.label = label
            self.result.value = value
            self.result.description = description
            return False
        if self.preprocessing_results["results"] == -2:
            # deletion of all data
            # "Mapping has happened in this region but data were deleted."
            label = "undefined"
            value = None
            description += self.metadata.label_description["undefined"]
            self.result.label = label
            self.result.value = value
            self.result.description = description
            return False
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
        # get y values fot best fitting sigmoid curve, with these y the
        # saturation will be calculated
        sigmoid_curve = sigmoidCurve()
        ydataForSat = sigmoid_curve.getBestFittingCurve(self.preprocessing_results)
        if ydataForSat[0] != "empty":
            # check if data are more than start stadium
            # The end of the start stage is defined with
            # the maximum of the curvature function f''(x)
            # here: simple check <= 2
            # TODO implement function from MA for start stadium
            """
            For buildings-count in a small area, this could return a wrong
            interpretation, eg a little collection of farm house and buildings
            with eg less than 8 buildings, but all buildings are mapped, the value
            would be red, but its all mapped...
            """
            # calculate/define traffic light value and label
            if max(df1.yValues) <= 2:
                # start stadium, some data are there, but not much
                label = "red"
                value = 0.0
                description += self.metadata.label_description["red"]
                self.saturation = 0
            else:
                # calculate slope/growth of last 3 years
                # take value in -36. month and value in last month of data
                earlyX = li[-36]
                lastX = li[-1]
                # get saturation level within last 3 years
                self.saturation = sigmoid_curve.getSaturationInLast3Years(
                    earlyX, lastX, df1.li, ydataForSat
                )
                # if earlyX and lastX return same y value
                # (means no growth any more), then
                # getSaturationInLast3Years returns 1.0

            # if saturation == 1.0:
            #    growth should be 0.0
            self.growth = 1 - self.saturation

            # growth is larger than 3% within last 3 years
            if self.growth <= THRESHOLD_YELLOW:
                label = "green"
                value = 1.0
                description += self.metadata.label_description["green"]
            else:
                # growth level is better than the red threshould
                label = "yellow"
                value = 0.5
                description += self.metadata.label_description["yellow"]
            description_template = Template(
                self.metadata.result_description
            ).substitute(saturation=self.saturation, growth=self.growth)
            description = description_template + " " + description
            self.result.label = label
            self.result.value = value
            self.result.description = description
            logging.debug(
                f"Saturation result value: {self.saturation}, label: {label},"
                f" value: {value}, description: {description}"
            )
        else:
            # no data / deletion of all data
            label = "undefined"
            value = None
            description += self.metadata.label_description["undefined"]
            self.result.label = label
            self.result.value = value
            self.result.description = description
            return False
        return True

    def create_figure(self) -> bool:
        """
        Create svg with data line in blue and sigmoid curve in red.
        """
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

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        # show nice dates on x axis in plot
        df1["timestamps"] = pd.to_datetime(df1["timestamps"])
        # plot the data
        ax.plot(
            df1.timestamps,
            df1.yValues,
            linecol[0],
            label="OSM data",
        )
        if ydataForSat[0] != "empty":
            ax.set_title("Saturation level of the data")
            # plot sigmoid curve
            ax.plot(df1.timestamps, ydataForSat, linecol[2], label="Sigmoid curve")
        elif self.preprocessing_results["results"] == -1:
            # start stadium
            # "No mapping has happened in this region. "
            plt.title(
                "No Sigmoid curve could be fitted into the data"
                + "\nNo mapping has happened in this region."
            )
        elif self.preprocessing_results["results"] == -2:
            # deletion of all data
            # "Mapping has happened in this region but data were deleted."
            plt.title(
                "No Sigmoid curve could be fitted into the data"
                + "\nMapping has happened but data were deleted."
            )
        else:
            plt.title("No Sigmoid curve could be fitted into the data")
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg", bbox_inches="tight")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
        return True
