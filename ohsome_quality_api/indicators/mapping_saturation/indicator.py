import logging
from string import Template

import numpy as np
import plotly.graph_objects as pgo
from dateutil.parser import isoparse
from geojson import Feature
from rpy2.rinterface_lib.embedded import RRuntimeError

from ohsome_quality_api.definitions import Color
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.indicators.mapping_saturation import models
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic, TopicData


class MappingSaturation(BaseIndicator):
    """The Mapping Saturation Indicator.

    Calculate the saturation within the last 3 years.
    Time period is one month since 2008.

    Premise: Each aggregation of features (e.g. length of roads or count of building)
    has a maximum. After increased mapping activity saturation is reached near this

    Different statistical models are used to find out if saturation is reached.
    maximum.

    Steps:
    1. Get the temporal evolution of OSM data
    2. Fit regression models using different logistic functions
    3. Choose the best-fit-model
    4. Estimate the total number (asymptote) based on the model parameters

    Reference Papers:
    - Gröchenig S et al. (2014): Digging into the history of VGI data-sets: results from
        a worldwide study on OpenStreetMap mapping activity
        (https://doi.org/10.1080/17489725.2014.978403)
    - Barrington-Leigh C and Millard-Ball A (2017): The world’s user-generated road map
        is more than 80% complete
        (https://doi.org/10.1371/journal.pone.0180698 pmid:28797037)
    - Josephine Brückner, Moritz Schott, Alexander Zipf, and Sven Lautenbach (2021):
        Assessing shop completeness in OpenStreetMap for two federal states in Germany
        /https://doi.org/10.5194/agile-giss-2-20-2021)
    """

    def __init__(
        self,
        topic: BaseTopic,
        feature: Feature,
        time_range: str = "2008-01-01//P1M",
    ) -> None:
        super().__init__(topic=topic, feature=feature)

        self.time_range: str = time_range

        # The following attributes will be set during the life-cycle of the object.
        # Attributes needed for calculation
        self.values: list = []
        self.timestamps: list = []

        self.upper_threshold = 0.97  # Threshold derived from Gröchenig et al.
        # TODO: What is a good lower threshold?
        self.lower_threshold = 0.30
        self.above_one_lower_threshold = 1.3
        self.above_one_upper_threshold = 1.5

        # Attributes needed for result determination
        self.best_fit: models.BaseStatModel | None = None
        self.fitted_models: list[models.BaseStatModel] = []

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            self.topic,
            self.feature,
            time=self.time_range,
        )
        for item in query_results["result"]:
            self.values.append(item["value"])
            self.timestamps.append(isoparse(item["timestamp"]))

    def calculate(self) -> None:  # noqa: C901
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
        if 1.0 >= self.result.value > self.upper_threshold:
            self.result.class_ = 5
        elif self.upper_threshold >= self.result.value > self.lower_threshold:
            self.result.class_ = 3
        elif self.lower_threshold >= self.result.value > 0:
            self.result.class_ = 1
        elif self.above_one_lower_threshold >= self.result.value > 1:
            self.result.class_ = 5
        elif (
            self.above_one_upper_threshold
            >= self.result.value
            > self.above_one_lower_threshold
        ):
            self.result.class_ = 3
        elif self.result.value > self.above_one_upper_threshold:
            self.result.class_ = 1
        else:
            raise ValueError(
                "Result value (saturation) is an unexpected value: {}".format(
                    self.result.value
                )
            )
        description = Template(self.templates.result_description).substitute(
            saturation=round(self.result.value * 100, 2)
        )
        self.result.description = (
            description + " " + self.templates.label_description[self.result.label]
        )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        fig = pgo.Figure()
        fig.add_trace(
            pgo.Scatter(
                x=self.timestamps,
                y=self.values,
                name="OSM data",
                line=dict(color=Color.BLUE.value),
            ),
        )
        fig.add_trace(
            pgo.Scatter(
                x=self.timestamps,
                y=self.best_fit.fitted_values.tolist(),
                name="Modelled saturation curve",
                line=dict(color=Color.RED.value),
            ),
        )
        fig.update_layout(title_text="Mapping Saturation")
        fig.update_xaxes(
            title_text="Date",
            ticks="outside",
        )
        if isinstance(self.topic, TopicData):
            fig.update_yaxes(title_text="Value")
        else:
            fig.update_yaxes(title_text=self.topic.aggregation_type.capitalize())

        # plot asymptote
        asymptote = self.data["best_fit"]["asymptote"]
        if asymptote < max(self.values) * 5:
            asymptote_line_values = [asymptote for _ in self.values]
            fig.add_trace(
                pgo.Scatter(
                    x=self.timestamps,
                    y=asymptote_line_values,
                    name="Estimated total data",
                    showlegend=True,
                    line=dict(color=Color.RED.value, dash="dash"),
                    hovertext=f"Estimated total data: {asymptote}",
                )
            )
            y_max = max(max(self.values), max(self.best_fit.fitted_values), asymptote)
            fig.update_yaxes(range=[min(self.values), y_max * 1.05])

        fig.update_layout(showlegend=True)
        # fixed legend, because we do not expect high contributions in 2008
        fig.update_legends(x=0.02, y=0.85, bgcolor="rgba(255,255,255,0.66)")

        fig.add_layout_image(
            dict(
                source="https://media.licdn.com/dms/image/v2/D560BAQE9rkvB7vB_cg/company-logo_200_200/company-logo_200_200/0/1711546373172/heigit_logo?e=2147483647&v=beta&t=pWdgVEOkz7VBhH2WbM5_DJeTs7RsdVXbolKU3ftS1iY",
                xref="paper",
                yref="paper",
                x=0.815,
                y=0.24,
                sizex=0.3,
                sizey=0.3,
                sizing="contain",
                opacity=0.3,
                layer="above",
            )
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
        fig.show()

    def check_edge_cases(self) -> str:
        """Check edge cases.

        Returns
            str: Returns description of edge case. Empty string if no edge is present.
        """
        if max(self.values) == 0:  # no data
            return "No features were mapped in this region."
        # TODO: Decide on the minimal number/length/area of features have to be present
        # to run models (#511).
        elif np.sum(self.values) < 10:  # not enough data
            return "Not enough data in total available in this region."
        elif len(self.values) < 36:  # not enough data points
            return (
                "Not enough data points available in this regions. "
                + "The Mapping Saturation indicator needs data for at least 36 months."
            )
        elif self.values[-1] == 0:  # data deleted
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
