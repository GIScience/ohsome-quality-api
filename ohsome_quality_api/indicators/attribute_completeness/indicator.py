import logging
from string import Template

import dateutil.parser
import plotly.graph_objs as go
from geojson import Feature

from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic as Topic


class AttributeCompleteness(BaseIndicator):
    def __init__(self, topic: Topic, feature: Feature) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.count_all = None
        self.count_match = None

    async def preprocess(self) -> None:
        query_results_count = await ohsome_client.query(
            self.topic,
            self.feature,
            ratio=True,
        )
        self.result.value = query_results_count["ratioResult"][0]["ratio"]
        self.count_all = query_results_count["ratioResult"][0]["value"]
        self.count_match = query_results_count["ratioResult"][0]["value2"]
        timestamp = query_results_count["ratioResult"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)

    def calculate(self) -> None:
        # self.result.value (ratio) can be of type float, NaN if no features of filter1
        # are in the region or None if the topic has no filter2
        if self.result.value == "NaN" or self.result.value is None:
            self.result.value = None
            return
        description = Template(self.metadata.result_description).substitute(
            result=round(self.result.value, 1),
            all=round(self.count_all, 1),
            matched=round(self.count_match, 1),
        )
        if self.count_all == 0:
            self.result.description = description + "No features in this region"
            return

        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        elif self.threshold_yellow > self.result.value >= self.threshold_red:
            self.result.class_ = 3
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
        else:
            self.result.class_ = 1
            self.result.description = (
                description + self.metadata.label_description["red"]
            )

    def create_figure(self) -> None:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        fig = go.Figure()

        # Plot inner Pie (Indicator Value)
        if type(self.result.value) == str:
            values = [1]
            labels = [""]
            marker_colors = ["white"]
        else:
            values = [self.result.value, 1 - self.result.value]
            labels = [
                f"{self.topic.name} <br> Ratio: {round(self.result.value, 2)}",
                "",
            ]
            marker_colors = ["black", "white"]

        fig.add_trace(
            go.Pie(
                values=values,
                labels=labels,
                sort=False,
                marker_colors=marker_colors,
                textinfo="none",
            )
        )

        # Plot outer Pie (Traffic Light)
        fig.add_trace(
            go.Pie(
                values=[0.25, 0.25, 0.50],
                labels=["Bad", "Good", "Medium"],
                marker_colors=["red", "green", "yellow"],
                hole=0.5,
                sort=False,
                textinfo="none",
            )
        )

        fig.update_layout(
            title={
                "text": "Ratio between all features and filtered ones",
                "y": 0.95,
                "x": 0.5,
                "yanchor": "top",
            },
            legend={
                "y": 0.5,
                "x": 0.75,
            },
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
