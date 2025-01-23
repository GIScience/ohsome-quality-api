import json
import logging
import os
from datetime import datetime, timezone
from string import Template

import dateutil
import plotly.graph_objects as go
from geojson import Feature

from ohsome_quality_api.attributes.definitions import (
    build_attribute_filter,
    get_attribute,
)
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import TopicDefinition as Topic
from ohsome_quality_api.trino import client as trino_client
from ohsome_quality_api.utils.helper_geo import get_bounding_box

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))


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
        trino: bool = False,  # Feature flag to use SQL instead of ohsome API queries
    ) -> None:
        super().__init__(topic=topic, feature=feature, trino=trino)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.attribute_keys = attribute_keys
        self.attribute_filter = attribute_filter
        self.attribute_title = attribute_title
        self.absolute_value_1: int | None = None
        self.absolute_value_2: int | None = None
        self.description = None
        if self.attribute_keys:
            self.attribute_filter = build_attribute_filter(
                self.attribute_keys,
                self.topic.key,
                self.trino,
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
                self.trino,
            )

    async def preprocess(self) -> None:
        if self.trino:
            file_path = os.path.join(WORKING_DIR, "query.sql")
            with open(file_path, "r") as file:
                sql_template = file.read()

            bounding_box = get_bounding_box(self.feature)
            geometry = json.dumps(self.feature["geometry"])

            sql = sql_template.format(
                bounding_box=bounding_box,
                geometry=geometry,
                filter=self.topic.sql_filter,
            )
            query = await trino_client.query(sql)
            results = await trino_client.fetch(query)
            # TODO: Check for None
            self.absolute_value_1 = results[0][0]

            sql = sql_template.format(
                bounding_box=bounding_box,
                geometry=geometry,
                filter=self.attribute_filter,
            )
            query = await trino_client.query(sql)
            results = await trino_client.fetch(query)
            self.absolute_value_2 = results[0][0]

            if self.absolute_value_1 is None and self.absolute_value_2 is None:
                self.result.value = None
            elif self.absolute_value_1 is None:
                raise ValueError("Unreachable code.")
            elif self.absolute_value_2 is None:
                self.result.value = 0
            else:
                self.result.value = self.absolute_value_2 / self.absolute_value_1

            # TODO: Query Trino for Timestamp
            self.result.timestamp_osm = datetime.now(timezone.utc)
        else:
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
        if self.result.value is None:
            raise TypeError("Result value should not be None.")
        else:
            result = round(self.result.value * 100, 1)
        if self.attribute_title is None:
            raise TypeError("Attribute title should not be None.")
        else:
            tags = str(
                "attributes " + self.attribute_title
                if self.attribute_keys and len(self.attribute_keys) > 1
                else "attribute " + self.attribute_title
            )
        all, matched = self.compute_units_for_all_and_matched()
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
            all = f"{str(round(self.absolute_value_1/1000000, 2))} km²"
            matched = f"{str(round(self.absolute_value_2/1000000, 2))} km²"
        elif self.topic.aggregation_type == "length":
            all = f"{str(round(self.absolute_value_1/1000, 2))} km"
            matched = f"{str(round(self.absolute_value_2/1000, 2))} km"
        else:
            raise ValueError("Invalid aggregation_type")
        return all, matched
