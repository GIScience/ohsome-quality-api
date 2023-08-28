import logging
from string import Template

import dateutil.parser
import numpy as np
import plotly.graph_objects as go
from geojson import Feature

from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic as Topic
from ohsome_quality_api.utils.helper_geo import calculate_area

# threshold values defining the color of the traffic light
# derived directly from sketchmap_fitness repo


class Density(BaseIndicator):
    def __init__(self, topic: Topic, feature: Feature) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow = 30
        self.threshold_red = 10
        self.area_sqkm = None
        self.count = None

    def green_threshold_function(self, area):
        return self.threshold_yellow * area

    def yellow_threshold_function(self, area):
        return self.threshold_red * area

    async def preprocess(self) -> None:
        query_results_count = await ohsome_client.query(self.topic, self.feature)
        self.area_sqkm = calculate_area(self.feature) / (1000 * 1000)
        self.count = query_results_count["result"][0]["value"]
        timestamp = query_results_count["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)

    def calculate(self) -> None:
        # TODO: we need to think about how we handle this
        #  if there are different topics
        self.result.value = self.count / self.area_sqkm  # density
        description = Template(self.metadata.result_description).substitute(
            result=f"{self.result.value:.2f}"
        )
        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        else:
            if self.result.value > self.threshold_red:
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
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        if self.area_sqkm < 10:
            max_area = 10
        else:
            max_area = round(self.area_sqkm * 2 / 10) * 10

        # Create x-axis data
        x = np.linspace(0, max_area, 2)

        # Calculate y-axis data for thresholds
        y1 = [self.green_threshold_function(xi) for xi in x]
        y2 = [self.yellow_threshold_function(xi) for xi in x]

        # Calculate y-axis data for fill_between areas
        fill_1 = np.maximum(y2, 0)
        fill_2 = np.maximum(y1, 0)
        fill_3 = np.maximum(y1[1], np.array([self.count, self.count]))

        # Create figure and add traces
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=x,
                y=fill_1,
                mode="lines",
                fill="tonexty",
                line=dict(color="red"),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=fill_2,
                mode="lines",
                fill="tonexty",
                line=dict(color="yellow"),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=fill_3,
                mode="lines",
                fill="tonexty",
                line=dict(color="green"),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y2,
                mode="lines",
                line=dict(dash="dot", color="black"),
                name="Threshold B",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y1,
                mode="lines",
                line=dict(dash="dash", color="black"),
                name="Threshold A",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[self.area_sqkm],
                y=[self.count],
                mode="markers",
                marker=dict(symbol="circle", size=10, color="black"),
                name="Location",
            )
        )
        # Update layout
        fig.update_layout(
            title="Density (Features per Area)",
            xaxis_title="Area (km²)",
            yaxis_title="Features",
        )
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
