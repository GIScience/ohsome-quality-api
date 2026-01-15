import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import plotly.graph_objects as pgo
from geojson import Feature
from plotly.subplots import make_subplots

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
    present_in_both_agree: int
    present_in_both_not_agree: int


class RoadsThematicAccuracy(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
        attribute: Literal["surface", "oneway", "lanes", "name", "width"] | None = None,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.attribute: str = attribute
        self.matched_data: MatchedData | None = None

    async def preprocess(self) -> None:
        if self.attribute is not None:
            with open(Path(__file__).parent / f"{self.attribute}.sql", "r") as file:
                query = file.read()
        else:
            with open(Path(__file__).parent / "all_attributes.sql", "r") as file:
                query = file.read()
        response = await client.fetch(query, str(self.feature["geometry"]))
        self.matched_data = MatchedData(
            total_dlm=response[0]["total_dlm"],
            both=response[0]["present_in_both"],
            only_dlm=response[0]["only_dlm"],
            only_osm=response[0]["only_osm"],
            missing_both=response[0]["missing_both"],
            present_in_both_agree=response[0]["present_in_both_agree"],
            present_in_both_not_agree=response[0]["present_in_both_not_agree"],
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

        # TODO: create plot if both is 0
        if self.matched_data.both > 0:
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
    values = [result.present_in_both_agree, result.present_in_both_not_agree]
    total = sum(values)
    if total > 0:
        text = [f"{v} ({v / total * 100:.1f}%)" for v in values]
    else:
        # TODO: handle case
        text = ""

    bar = pgo.Bar(
        x=labels,
        y=values,
        text=text,
        textposition="auto",
        marker_color="salmon",
        name="Value",
    )
    return bar
