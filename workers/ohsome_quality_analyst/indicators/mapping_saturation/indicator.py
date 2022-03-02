import logging
from io import StringIO
from string import Template
from typing import List, Optional, Union

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

    Calculate the saturation within the last 3 years.
    Time period is one month since 2008.

    Premise: Each aggregation of features (e.g. length of roads or count of building)
    has a maximum. After increased mapping activity saturation is reached near this
    maximum.

    Different statistical models are used to find out if saturation is reached.

    Reference Papers:
    - Gröchenig S et al. (2014): Digging into the history of VGI data-sets: results from
        a worldwide study on OpenStreetMap mapping activity
        (https://doi.org/10.1080/17489725.2014.978403)
    - Barrington-Leigh C and Millard-Ball A (2017): The world’s user-generated road map
        is more than 80% complete
        (https://doi.org/10.1371/journal.pone.0180698 pmid:28797037)
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
        self.latest_value: Union[None, int, float] = None
        self.timestamps: list = []

        self.upper_threshold = 0.97  # Threshold derived from Gröchenig et al.
        # TODO: What is a good lower threshold?
        self.lower_threshold = 0.30

        # Attributes needed for result determination
        self.best_fit: Optional[models.BaseStatModel] = None
        self.fitted_models: List[models.BaseStatModel] = []

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            layer=self.layer,
            bpolys=self.feature.geometry,
            time=self.time_range,
        )
        for item in query_results["result"]:
            self.values.append(item["value"])
            self.timestamps.append(isoparse(item["timestamp"]))
        self.latest_value = self.values[-1]

    def calculate(self) -> None:
        # Latest timestamp of ohsome API results
        self.result.timestamp_osm = self.timestamps[-1]
        edge_case_description = self.check_edge_cases()
        if edge_case_description:
            logging.info("Edge case is present. Skipping indicator calculation.")
            self.result.description = edge_case_description
            return
        xdata = np.array(range(len(self.timestamps)))
        fitted_models = []
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
                fitted_models.append(model(xdata=xdata, ydata=np.array(self.values)))
            # RRuntimeError can occur if data can not be modeled by the R model
            except RRuntimeError as error:
                logging.info(
                    'Skipping model "{0}" due to RRuntimeError: {1}'.format(
                        model.name, str(error).strip()
                    )
                )
                continue
            # RuntimeError can occur if data could not be modeled by `curve_fit` (scipy)
            except RuntimeError as error:
                logging.info(
                    'Skipping model "{0}" due to RuntimeError: {1}'.format(
                        model.name, str(error).strip()
                    )
                )
                continue
        self.fitted_models = self.select_models(fitted_models)
        if not self.fitted_models:
            logging.info("No model has been run successfully.")
            return
        self.best_fit = min(self.fitted_models, key=lambda m: m.mae)
        logging.info("Best fitting model: " + self.best_fit.name)
        # Saturation of the last 3 years of the fitted curve
        y1 = np.interp(xdata[-36], xdata, self.best_fit.fitted_values)
        y2 = np.interp(xdata[-1], xdata, self.best_fit.fitted_values)
        self.result.value = y1 / y2  # Saturation
        description = Template(self.metadata.result_description).substitute(
            saturation=round(self.result.value * 100, 2)
        )
        if 1.0 >= self.result.value > self.upper_threshold:
            self.result.label = "green"
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        elif self.upper_threshold >= self.result.value > self.lower_threshold:
            self.result.label = "yellow"
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
        elif self.lower_threshold >= self.result.value > 0:
            self.result.label = "red"
            self.result.description = (
                description + self.metadata.label_description["red"]
            )
        else:
            self.result.description = (
                "The result value (saturation) is an unexpected value."
            )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        ax.set_title("Mapping Saturation")
        ax.plot(
            self.timestamps,
            self.values,
            label="OSM data",
        )
        ax.plot(
            self.timestamps,
            self.best_fit.fitted_values,
            label=self.best_fit.name,
        )
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg", bbox_inches="tight")
        self.result.svg = img_data.getvalue()
        logging.info("Successful creation of the SVG figure.")
        plt.close("all")

    def check_edge_cases(self) -> str:
        """Check edge cases

        Returns
            str: Returns description of edge case. Empty string if no edge is present.
        """
        # TODO: Add check for the case where the history is to short
        # no data
        if max(self.values) == 0:
            return "No features were mapped in this region."
        # TODO: Decide on how many features have to be present to run models.
        # Values can be a count of features (building )or length of features (streets)
        # not enough data
        elif np.sum(self.values) < 10:
            return "Not enough data in this regions available."
        # deleted data
        elif self.latest_value == 0:
            return "All mapped features in this region have been deleted."
        return ""

    def select_models(self, fitted_models) -> list:
        """Select suitable models

        Selection criteria:
            1. Decrease in curve growth
                - The last data point should be after the inflection point of the curve
                - If no inflection point exists other measures are used which
                    approximates 50% of asymptote.
            2. Data is below 95% confidence interval of the asymptote
                - Check if the latest data (average last two years) is lower than the
                    upper limit of the 95% confidence interval of the estimated
                    asymptote
        """
        for fm in list(fitted_models):
            if fm.name == "Nls Michaelis-Menten Model":
                param = fm.coefficients["K"]
            elif fm.name == "Nls Asymptotic Regression Model":
                param = (fm.coefficients["asym"] + fm.coefficients["R0"]) / 2
            else:
                param = fm.inflection_point
            xdata_max = len(self.timestamps)
            if xdata_max <= param:
                fitted_models.remove(fm)

        avg_last_2_years = np.sum(self.values[-24]) / 24
        for fm in list(fitted_models):
            if avg_last_2_years >= fm.asym_conf_int[1]:
                fitted_models.remove(fm)

        return fitted_models
