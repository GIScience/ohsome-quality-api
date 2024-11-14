import logging
from string import Template

import dateutil.parser
import plotly.graph_objects as go
from geojson import Feature

from ohsome_quality_api.attributes.definitions import (
    build_attribute_filter,
    get_attribute,
)
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic as Topic


class AttributeCompleteness(BaseIndicator):
    """
    Attribute completeness of map features.

    The ratio of features of a given topic to features of the same topic with additional
    (expected) attributes.

    Terminology:
        topic: Category of map features. Translates to a ohsome filter.
        attribute: Additional (expected) tag(s) describing a map feature.
            attribute_keys: a set of predefined attributes wich will be
                translated to an ohsome filter
            attribute_filter: a custom ohsome filter

    Example: How many buildings (topic) have height information (attribute)?

    Premise: Every map feature of a given topic should have certain additional
        attributes.

    Limitation: Limited to one attribute.
    """

    # TODO make attribute a list
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
        attribute_keys: list[str] | None = None,
        attribute_filter: str | None = None,
        attribute_names: list[str] | None = None,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.attribute_keys = attribute_keys
        self.attribute_filter = attribute_filter
        self.attribute_names = attribute_names
        self.absolute_value_1 = None
        self.absolute_value_2 = None
        self.description = None
        # fmt: off
        # TODO: Remove once validated by pydantic request model
        if (
            all(v is None for v in (attribute_keys, attribute_filter)) or
            all(v is not None for v in (attribute_keys, attribute_filter))
        ):
            raise TypeError(
                "Either `attribute_keys` or `attribute_filter` needs to be given"
            )
        # fmt: on
        if self.attribute_keys:
            self.attribute_filter = build_attribute_filter(
                self.attribute_keys,
                self.topic.key,
            )
            self.attribute_names = [
                get_attribute(self.topic.key, k).name.lower()
                for k in self.attribute_keys
            ]

    async def preprocess(self) -> None:
        # Get attribute filter
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            attribute_filter=self.attribute_filter,
        )
        timestamp = response["ratioResult"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        self.result.value = response["ratioResult"][0]["ratio"]
        self.absolute_value_1 = response["ratioResult"][0]["value"]
        self.absolute_value_2 = response["ratioResult"][0]["value2"]

    def calculate(self) -> None:
        # result (ratio) can be NaN if no features matching filter1
        if self.result.value == "NaN":
            self.result.value = None
        if self.result.value is None:
            self.result.description += " No features in this region"
            return
        self.create_description()

        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                self.description + self.templates.label_description["green"]
            )
        elif self.threshold_yellow > self.result.value >= self.threshold_red:
            self.result.class_ = 3
            self.result.description = (
                self.description + self.templates.label_description["yellow"]
            )
        else:
            self.result.class_ = 1
            self.result.description = (
                self.description + self.templates.label_description["red"]
            )

    def create_description(self):
        all, matched = self.compute_units_for_all_and_matched()
        if self.result.value is None:
            raise TypeError("result value should not be None")
        else:
            result = round(self.result.value * 100, 1)
        if len(self.attribute_names) > 1:
            tags = "attributes " + ", ".join(self.attribute_names)
        else:
            tags = "attribute " + self.attribute_names[0]
        self.description = Template(self.templates.result_description).substitute(
            result=result,
            all=all,
            matched=matched,
            topic=self.topic.name.lower(),
            tags=tags,
        )

    def create_figure(self) -> None:
        """Create a gauge chart.

        The gauge chart shows the percentage of features having the requested
        attribute(s).
        """
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        fig = go.Figure(
            go.Indicator(
                domain={"x": [0, 1], "y": [0, 1]},
                mode="gauge+number",
                value=self.result.value * 100,
                number={"suffix": "%"},
                type="indicator",
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickwidth": 1,
                        "tickcolor": "darkblue",
                        "ticksuffix": "%",
                        "tickfont": dict(color="black", size=20),
                    },
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, self.threshold_red * 100], "color": "tomato"},
                        {
                            "range": [
                                self.threshold_red * 100,
                                self.threshold_yellow * 100,
                            ],
                            "color": "gold",
                        },
                        {
                            "range": [self.threshold_yellow * 100, 100],
                            "color": "darkseagreen",
                        },
                    ],
                },
            )
        )

        fig.update_layout(
            font={"color": "black", "family": "Arial"},
            xaxis={"showgrid": False, "range": [-1, 1], "fixedrange": True},
            yaxis={"showgrid": False, "range": [0, 1], "fixedrange": True},
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=True,
        )

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def compute_units_for_all_and_matched(self):
        if self.topic.aggregation_type == "count":
            all = f"{int(self.absolute_value_1)} elements"
            matched = f"{int(self.absolute_value_2)} elements"
        elif self.topic.aggregation_type == "area":
            all = f"{str(round(self.absolute_value_1, 2))} m²"
            matched = f"{str(round(self.absolute_value_2, 2))} m²"
        elif self.topic.aggregation_type == "length":
            all = f"{str(round(self.absolute_value_1, 2))} m"
            matched = f"{str(round(self.absolute_value_2, 2))} m"
        else:
            raise ValueError("Invalid aggregation_type")
        return all, matched
