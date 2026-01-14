import logging
from dataclasses import dataclass
from pathlib import Path

import plotly.graph_objects as pgo
from geojson import Feature
from plotly.subplots import make_subplots

from ohsome_quality_api.api.request_models import RoadsThematicAccuracyAttribute
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import Topic

logger = logging.getLogger(__name__)


@dataclass
class MatchedData:
    total_dlm: int
    both: int
    only_dlm: int
    only_osm: int
    missing_both: int
    same_value: int
    different_value: int


attribute_mapping = {
    RoadsThematicAccuracyAttribute.ONEWAY: "oneway",
    RoadsThematicAccuracyAttribute.LANES: "lanes",
    RoadsThematicAccuracyAttribute.SURFACE: "surface",
    RoadsThematicAccuracyAttribute.NAME: "name",
    RoadsThematicAccuracyAttribute.WIDTH: "width",
}


class RoadsThematicAccuracy(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
        attribute: RoadsThematicAccuracyAttribute | None = None,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )
        self.attribute = attribute

    async def preprocess(self) -> None:
        if self.attribute is not None:
            with open(
                Path(__file__).parent / f"{attribute_mapping[self.attribute]}.sql", "r"
            ) as file:
                query = file.read()
        else:
            with open(Path(__file__).parent / "all_attributes.sql", "r") as file:
                query = file.read()
        response = await client.fetch(query, str(self.feature["geometry"]))
        self.matched_data = MatchedData(
            total_dlm=response[0][0],
            both=response[0][1],
            only_dlm=response[0][2],
            only_osm=response[0][3],
            missing_both=response[0][4],
            same_value=response[0][5],
            different_value=response[0][6],
        )
        # TODO: get timestamps

    def calculate(self) -> None:
        self.result.value = None  # TODO: do we want a result value
        label_description = getattr(self.templates.label_description, self.result.label)
        self.result.description = "\n" + label_description

    def create_figure(self) -> None:
        if self.matched_data.total_dlm == 0:
            return
        fig = make_subplots(
            rows=1, cols=2, subplot_titles=("Presence (DLM vs OSM)", "Value Comparison")
        )

        fig.add_trace(plot_presence(self.matched_data), row=1, col=1)
        fig.add_trace(plot_value_comparison(self.matched_data), row=1, col=2)

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


def plot_presence(result: MatchedData) -> pgo.Bar:
    """
    Return a Plotly Bar trace for presence comparison.
    """
    labels = ["Both", "Only DLM", "Only OSM", "Missing both"]
    values = [result.both, result.only_dlm, result.only_osm, result.missing_both]
    total = sum(values)
    text = [f"{v} ({v / total * 100:.1f}%)" for v in values]

    bar = pgo.Bar(
        x=labels,
        y=values,
        text=text,
        textposition="auto",
        marker_color="skyblue",
        name="Presence",
    )
    return bar


def plot_value_comparison(result: MatchedData) -> pgo.Bar:
    labels = ["Same value", "Different value"]
    values = [result.same_value, result.different_value]
    total = sum(values)
    text = [f"{v} ({v / total * 100:.1f}%)" for v in values]

    bar = pgo.Bar(
        x=labels,
        y=values,
        text=text,
        textposition="auto",
        marker_color="salmon",
        name="Value",
    )
    return bar
