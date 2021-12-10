import logging
from io import StringIO
from string import Template
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import isoparse
from geojson import Feature
from rpy2.rinterface_lib.embedded import RRuntimeError

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.indicators.mapping_saturation import models
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
        # Threshold derived from MA Katha p24
        # (mixture of Gröchenig et al. +  Barrington-Leigh)
        # saturation: 0 < f‘(x) <= 0.03 and years with saturation > 2
        self.threshold_yellow = 0.03
        # TODO: THRESHOLD_RED (where start stadium ends) with function from MA Katha p24
        # self.threshold_red = None

        # Attributes needed for result determination
        self.best_fit: Optional[models.BaseStatModel] = None
        self.fitted_models: List[models.BaseStatModel] = []
        self.saturation: Optional[float] = None
        self.growth: Optional[float] = None

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            layer=self.layer,
            bpolys=self.feature.geometry,
            time=self.time_range,
        )
        for item in query_results["result"]:
            self.values.append(item["value"])
            self.timestamps.append(isoparse(item["timestamp"]))

    def calculate(self) -> None:
        # Latest timestamp of ohsome API results
        self.result.timestamp_osm = self.timestamps[-1]
        if not self.check_corner_cases():
            return
        xdata = np.asarray(range(len(self.timestamps)))
        for model in (
            models.Sigmoid,
            models.SSlogis,
            models.SSdoubleS,
            models.SSfpl,
            models.SSasymp,
            models.SSmicmen,
        ):
            logging.info("Run {}".format(model.name))
            try:
                self.fitted_models.append(
                    model(xdata=xdata, ydata=np.asarray(self.values))
                )
            except RRuntimeError as error:
                logging.warning(
                    "Could not run model {0} due to RRuntimeError: {1}".format(
                        model.name, error
                    )
                )
                continue
        self.best_fit = min(self.fitted_models, key=lambda m: m.mae)
        logging.info("Best fitting model: " + self.best_fit.name)
        self.saturation = (
            np.interp(xdata[-36], xdata, self.best_fit.fitted_values)
        ) / (np.interp(xdata[-1], xdata, self.best_fit.fitted_values))
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
            self.best_fit.fitted_values,
            linecol[2],
            label="Sigmoid curve: " + self.best_fit.name,
        )
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg", bbox_inches="tight")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")

    def check_corner_cases(self) -> bool:
        """Check corner cases

        If corner case is present set result description.

        Returns
            bool: Return True if no corner case present. False otherwise.
        """
        # TODO: Add logs
        # no data
        if max(self.values) == 0:
            self.result.description = "No features were mapped in this region."
            return False
        # TODO: Decide on how many features have to be present to run models.
        # not enough data
        elif np.sum(self.values) < 10:
            self.corner_case = "not_enough_data"
            return False
        # deleted data
        elif self.values[-1] == 0:
            self.result.description = (
                "All mapped features in this region have been deleted."
            )
            return False
        return True
