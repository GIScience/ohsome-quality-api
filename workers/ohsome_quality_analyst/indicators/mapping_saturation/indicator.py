import logging
from io import StringIO
from string import Template

import matplotlib.pyplot as plt
from dateutil.parser import isoparse
from geojson import Feature

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
    """The Mapping Saturation Indicator.

    Time period is one month since 2008.
    """

    def __init__(
        self,
        layer_name: str,
        feature: Feature,
        time_range: str = "2008-01-01//P1M",
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            feature=feature,
        )
        self.time_range = time_range
        # Following attributes will be set during life-cycle of the object.
        # Attributes needed for calculation
        self.values: list = []
        self.values_normalized: list = []
        self.timestamps: list = []
        self.no_data: bool = False
        self.deleted_data: bool = False

        # Attributes needed for result determination
        self.saturation = None
        self.growth = None

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=self.feature.geometry, time=self.time_range
        )
        self.values = [item["value"] for item in query_results["result"]]
        self.timestamps = [
            isoparse(item["timestamp"]) for item in query_results["result"]
        ]
        # Latest timestamp of ohsome API results
        self.result.timestamp_osm = max(self.timestamps)
        max_value = max(self.values)
        if max_value == 0:
            self.no_data = True
        # TODO: Are query_results/values sorted after time?
        elif self.values[-1] == 0:
            self.deleted_data = True
        else:
            self.values_normalized = [value / max_value for value in self.values]

    def calculate(self) -> None:
        """Calculate the growth rate + saturation level within the last 3 years."""
        if self.no_data:
            self.result.description = "No mapping has occurred in this region."
            return
        if self.deleted_data:
            self.result.description = (
                "Mapping has occurred in this region but has been deleted since."
            )
            return
        # prepare the data
        li = list(range(len(self.values)))

        # get y values fot best fitting sigmoid curve, with these y the
        # saturation will be calculated
        sigmoid_curve = sigmoidCurve()
        ydata_for_sat = sigmoid_curve.getBestFittingCurve(
            {
                "timestamps": self.timestamps,
                "results": self.values,
                "results_normalized": self.values_normalized,
            }
        )
        if ydata_for_sat[0] != "empty":
            # check if data are more than start stadium
            # The end of the start stage is defined with
            # the maximum of the curvature function f''(x)
            # here: simple check <= 2
            # TODO implement function from MA for start stadium
            #
            # For buildings-count in a small area, this could return a wrong
            # interpretation, eg a little collection of farm house and buildings
            # with eg less than 8 buildings, but all buildings are mapped, the value
            # would be red, but its all mapped...
            # calculate/define traffic light value and label
            if max(self.values) <= 2:
                # start stadium, some data are there, but not much
                self.saturation = 0
            else:
                # calculate slope/growth of last 3 years
                # take value in -36. month and value in last month of data
                early_x = li[-36]
                last_x = li[-1]
                # get saturation level within last 3 years
                self.saturation = sigmoid_curve.getSaturationInLast3Years(
                    early_x, last_x, li, ydata_for_sat
                )
                # if earlyX and lastX return same y value
                # (means no growth any more), then
                # getSaturationInLast3Years returns 1.0

            # if saturation == 1.0:
            #    growth should be 0.0
            self.growth = 1 - self.saturation

            description = Template(self.metadata.result_description).substitute(
                saturation=self.saturation,
                growth=self.growth,
            )
            if self.saturation == 0:
                self.result.label = "red"
                self.result.value = 0.0
                self.result.description = (
                    description + self.metadata.label_description["red"]
                )
            # growth is larger than 3% within last 3 years
            elif self.growth <= THRESHOLD_YELLOW:
                self.result.label = "green"
                self.result.value = 1.0
                self.result.description = (
                    description + self.metadata.label_description["green"]
                )
            # growth level is better than the red threshould
            else:
                self.result.label = "yellow"
                self.result.value = 0.5
                self.result.description = (
                    description + self.metadata.label_description["yellow"]
                )

    def create_figure(self) -> None:
        """Create svg with data line in blue and sigmoid curve in red."""
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        # prepare plot
        # color the lines with different colors
        linecol = ["b-", "g-", "r-", "y-", "black", "gray", "m-", "c-"]

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        # plot the data
        ax.plot(
            self.timestamps,
            self.values,
            linecol[0],
            label="OSM data",
        )

        sigmoid_curve = sigmoidCurve()
        ydata_for_sat = sigmoid_curve.getBestFittingCurve(
            {
                "timestamps": self.timestamps,
                "results": self.values,
                "results_normalized": self.values_normalized,
            }
        )
        if ydata_for_sat[0] != "empty":
            ax.set_title("Saturation level of the data")
            # plot sigmoid curve
            ax.plot(
                self.timestamps,
                ydata_for_sat,
                linecol[2],
                label="Sigmoid curve",
            )
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg", bbox_inches="tight")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
