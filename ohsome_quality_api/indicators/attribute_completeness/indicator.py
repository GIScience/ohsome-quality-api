import logging
from string import Template

import dateutil.parser
import plotly.graph_objects as go
from babel.numbers import format_decimal, format_percent
from fastapi_i18n import _, get_locale
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
            attribute_filter: ohsome filter query representing custom attributes
            attribute_title:  Title describing the attributes represented by
                the Attribute Filter

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
        attribute_title: str | None = None,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.attribute_keys = attribute_keys
        self.attribute_filter = attribute_filter
        self.attribute_title = attribute_title
        self.absolute_value_1 = None
        self.absolute_value_2 = None
        self.description = None
        if self.attribute_keys:
            self.attribute_filter = build_attribute_filter(
                self.attribute_keys,
                self.topic.key,
            )
            self.attribute_title = ", ".join(
                [
                    get_attribute(self.topic.key, k).name.lower()
                    for k in self.attribute_keys
                ]
            )
        else:
            self.attribute_filter = build_attribute_filter(
                self.attribute_filter,
                self.topic.key,
            )

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
            self.result.description += _(" No features in this region")
            return
        self.create_description()

        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                self.description + self.templates.label_description.green
            )
        elif self.threshold_yellow > self.result.value >= self.threshold_red:
            self.result.class_ = 3
            self.result.description = (
                self.description + self.templates.label_description.yellow
            )
        else:
            self.result.class_ = 1
            self.result.description = (
                self.description + self.templates.label_description.red
            )

    def create_description(self):
        if self.result.value is None:
            raise TypeError(_("Result value should not be None."))
        else:
            result = format_percent(round(self.result.value, 1), locale=get_locale())
        if self.attribute_title is None:
            raise TypeError(_("Attribute title should not be None."))
        else:
            tags = str(
                _("attributes ") + self.attribute_title
                if self.attribute_keys and len(self.attribute_keys) > 1
                else _("attribute ") + self.attribute_title
            )
        all_, matched = self.compute_units_for_all_and_matched()
        self.description = Template(self.templates.result_description).substitute(
            result=result,
            all=all_,
            matched=matched,
            topic=self.topic.name,
            tags=tags,
        )

    def create_figure(self) -> None:
        """Create a gauge chart.

        The gauge chart shows the percentage of features having the requested
        attribute(s).
        """
        if self.result.label == "undefined":
            logging.info(_("Result is undefined. Skipping figure creation."))
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
            all_ = _("{absolute_value} elements").format(
                absolute_value=int(self.absolute_value_1)
            )
            matched = f"{int(self.absolute_value_2)} {_('elements')}"
        elif self.topic.aggregation_type == "area":
            all_ = f"{
                format_decimal(
                    round(self.absolute_value_1 / 1000000, 2), locale=get_locale()
                )
            } km²"
            matched = f"{
                format_decimal(
                    round(self.absolute_value_2 / 1000000, 2), locale=get_locale()
                )
            } km²"
        elif self.topic.aggregation_type == "length":
            all_ = f"{
                format_decimal(
                    round(self.absolute_value_1 / 1000, 2), locale=get_locale()
                )
            } km"
            matched = f"{
                format_decimal(
                    round(self.absolute_value_2 / 1000, 2), locale=get_locale()
                )
            } km"
        else:
            raise ValueError(_("Invalid aggregation_type"))
        return all_, matched
