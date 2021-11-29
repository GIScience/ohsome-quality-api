import logging
from io import StringIO
from string import Template
from typing import Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import isoparse
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.indicators.mapping_saturation.fit import (
    Fit,
    get_best_fit,
    run_all_models,
)
from ohsome_quality_analyst.ohsome import client as ohsome_client


class MappingSaturation(BaseIndicator):
    """The Mapping Saturation Indicator.

    Calculate the growth rate and saturation level within the last 3 years.
    Time period is one month since 2008.

    Method is based on Barrington-Leigh C and Millard-Ball A (2017):
    The world’s user-generated road map is more than 80% complete
    https://doi.org/10.1371/journal.pone.0180698 pmid:28797037
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
        self.time_range: str = time_range
        # The following attributes will be set during the life-cycle of the object.
        # Attributes needed for calculation
        self.values: list = []
        self.timestamps: list = []
        self.corner_cases: Literal["", "no_data", "deleted_data"] = ""
        # Threshold derived from MA Katha p24
        # (mixture of Gröchenig et al. +  Barrington-Leigh)
        # saturation: 0 < f‘(x) <= 0.03 and years with saturation > 2
        self.threshold_yellow = 0.03
        # TODO: THRESHOLD_RED (where start stadium ends) with function from MA Katha p24
        # self.threshold_red = None

        # Attributes needed for result determination
        self.best_fit: Optional[Fit] = None
        self.saturation: Optional[float] = None
        self.growth: Optional[float] = None

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=self.feature.geometry, time=self.time_range
        )
        self.values = [item["value"] for item in query_results["result"]]
        self.timestamps = [
            isoparse(item["timestamp"]) for item in query_results["result"]
        ]
        max_value = max(self.values)
        if max_value == 0:
            self.no_data = True
        elif self.values[-1] == 0:
            self.deleted_data = True

    def calculate(self) -> None:
        # Latest timestamp of ohsome API results
        self.result.timestamp_osm = self.timestamps[-1]
        if self.corner_cases == "no_data":
            self.result.description = "No features were mapped in this region."
            return
        if self.corner_cases == "deleted_data":
            self.result.description = (
                "All mapped features in this region have been since deleted."
            )
            return
        xdata = np.asarray(list(range(len(self.timestamps))))
        fits = run_all_models(xdata=xdata, ydata=np.asarray(self.values))
        self.best_fit = get_best_fit(fits)
        logging.info("Best fitting sigmoid curve: " + self.best_fit.model_name)
        # TODO: Following condition is a corner case and
        # should be handled before running models.
        if max(self.values) <= 2:
            # Some data are there, but not much -> start stadium
            self.saturation = 0
        else:
            # Calculate slope of last 3 years (saturation)
            self.saturation = (np.interp(xdata[-36], xdata, self.best_fit.ydata)) / (
                np.interp(xdata[-1], xdata, self.best_fit.ydata)
            )
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
        elif self.growth <= self.threshold_yellow:
            self.result.label = "green"
            self.result.value = 1.0
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        else:
            self.result.label = "yellow"
            self.result.value = 0.5
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        # color the lines with different colors
        linecol = ["b-", "g-", "r-", "y-", "black", "gray", "m-", "c-"]
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        ax.set_title("Saturation level of the data")
        # plot the data
        ax.plot(
            self.timestamps,
            self.values,
            linecol[0],
            label="OSM data",
        )
        # plot sigmoid curve
        ax.plot(
            self.timestamps,
            self.best_fit.ydata,
            linecol[2],
            label="Sigmoid curve: " + self.best_fit.model_name,
        )
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg", bbox_inches="tight")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
