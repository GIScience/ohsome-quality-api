import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from typing import Literal

import geojson
import plotly.graph_objects as pgo
from babel.numbers import format_percent
from fastapi_i18n import _, get_locale
from geojson import Feature
from plotly.subplots import make_subplots

from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import Topic

logger = logging.getLogger(__name__)


@dataclass
class MatchedData:
    total_dlm: float
    present_in_both: float
    only_dlm: float
    only_osm: float
    missing_both: float
    present_in_both_agree: float
    present_in_both_not_agree: float
    not_matched: float


class RoadsThematicAccuracy(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
        attribute: Literal["surface", "oneway", "lanes", "name", "width"] | None = None,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.attribute: str | None = attribute
        self.matched_data: MatchedData | None = None

    @classmethod
    async def coverage(cls, inverse=False) -> list[Feature]:
        # TODO: do we want two separate coverages for Germany?
        if inverse:
            query = (
                "SELECT ST_AsGeoJSON(inversed) FROM osm_corine_intersection_coverage"
            )
        else:
            query = "SELECT ST_AsGeoJSON(simple) FROM osm_corine_intersection_coverage"
        result = await client.fetch(query)
        return [Feature(geometry=geojson.loads(result[0][0]))]

    async def preprocess(self) -> None:
        if self.attribute is not None:
            with open(
                Path(__file__).parent / "queries" / f"{self.attribute}.sql", "r"
            ) as file:
                query = file.read()
        else:
            with open(
                Path(__file__).parent / "queries" / "all_attributes.sql", "r"
            ) as file:
                query = file.read()
        response = await client.fetch(query, str(self.feature["geometry"]))
        # TODO: check if response is not none
        self.matched_data = MatchedData(
            total_dlm=response[0]["total_dlm"],
            present_in_both=response[0]["present_in_both"],
            only_dlm=response[0]["only_dlm"],
            only_osm=response[0]["only_osm"],
            missing_both=response[0]["missing_both"],
            present_in_both_agree=response[0]["present_in_both_agree"],
            present_in_both_not_agree=response[0]["present_in_both_not_agree"],
            not_matched=response[0]["not_matched"],
        )
        # TODO: take real timestamps from data
        self.dlm_timestamp = datetime(2021, 1, 1, tzinfo=timezone.utc)
        self.result.timestamp_osm = datetime.now(timezone.utc)

    def calculate(self) -> None:
        self.result.value = None  # TODO: do we want a result value
        description = ""
        if self.matched_data.total_dlm is None:
            self.result.description = "No data in the area of interest."
            return
        if self.matched_data.total_dlm > 0:
            percentage = format_percent(
                1 - (self.matched_data.not_matched / self.matched_data.total_dlm),
                format="##0.#%",
                locale=get_locale(),
            )
            description += _(
                " The graph on the left shows information for the presence "
                "of attributes in the two datasets."
            )
            if self.matched_data.present_in_both > 0:
                description += _(
                    " The right graphs shows the agreement for all "
                    "elements that contain the selected attribute(s) "
                    "in both datasets."
                )
            else:
                description += _(
                    " There are no matched roads where the"
                    " selected attribute(s) are present in both datasets"
                )

        else:
            percentage = format_percent(0, locale=get_locale())
        self.result.description = (
            Template(self.templates.result_description).safe_substitute(
                {
                    "attribute": f"'{self.attribute.capitalize()}'"
                    if self.attribute is not None
                    else _("'All attributes'"),
                    "percent": percentage,
                }
            )
            + description
        )

    def create_figure(self) -> None:
        if self.matched_data.total_dlm is None or self.matched_data.total_dlm == 0:
            return

        fig = make_subplots(
            rows=1,
            cols=2,
        )

        fig.add_trace(plot_presence(self.matched_data), row=1, col=1)

        # TODO: create plot if both is 0
        if self.matched_data.present_in_both > 0:
            fig.add_trace(plot_value_comparison(self.matched_data), row=1, col=2)

        fig.update_layout(
            {
                "annotations": [
                    {
                        "text": (
                            f"<span style='font-size:smaller'>"
                            f"{_('DLM data from')} "
                            f"{self.dlm_timestamp.strftime('%Y')}"
                            f"</span>"
                            f"<br>"
                            f"<span style='font-size:smaller'>"
                            f"{_('OSM data from')} "
                            f"{self.result.timestamp_osm.strftime('%Y')}"
                            f"</span>"
                        ),
                        "xref": "paper",
                        "yref": "paper",
                        "x": 1.1,
                        "y": 0.8,
                        "yanchor": "top",
                        "showarrow": False,
                        "align": "left",
                    }
                ],
            }
        )
        fig.update_yaxes(rangemode="nonnegative")
        fig.update_xaxes(rangemode="nonnegative")

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


def plot_presence(result: MatchedData) -> pgo.Bar:
    labels = [_("Both"), _("Only DLM"), _("Only OSM"), _("Missing both")]
    values = [
        round(result.present_in_both, 2),
        round(result.only_dlm, 2),
        round(result.only_osm, 2),
        round(result.missing_both, 2),
    ]
    total = sum(values)
    text = [
        f"{v} ({format_percent(v / total, format='##0.#%', locale=get_locale())})"
        for v in values
    ]

    bar = pgo.Bar(
        x=labels,
        y=values,
        text=text,
        textposition="auto",
        marker_color="skyblue",
        name=_("Presence"),
    )
    return bar


def plot_value_comparison(result: MatchedData) -> pgo.Bar:
    labels = [_("Same value"), _("Different value")]
    values = [
        round(result.present_in_both_agree, 2),
        round(result.present_in_both_not_agree, 2),
    ]
    total = sum(values)
    text = (
        [
            f"{v} ({format_percent(v / total, format='##0.#%', locale=get_locale())})"
            for v in values
        ]
        if total > 0
        else ""
    )
    bar = pgo.Bar(
        x=labels,
        y=values,
        text=text,
        textposition="auto",
        marker_color="salmon",
        name=_("Value"),
    )
    return bar
