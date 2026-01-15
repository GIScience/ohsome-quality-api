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
    both: float
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
        self.matched_data = MatchedData(
            total_dlm=round(response[0]["total_dlm"], 2),
            both=round(response[0]["present_in_both"], 2),
            only_dlm=round(response[0]["only_dlm"], 2),
            only_osm=round(response[0]["only_osm"], 2),
            missing_both=round(response[0]["missing_both"], 2),
            present_in_both_agree=round(response[0]["present_in_both_agree"], 2),
            present_in_both_not_agree=round(
                response[0]["present_in_both_not_agree"], 2
            ),
            not_matched=round(response[0]["not_matched"], 2),
        )
        # TODO: take real timestamps from data
        self.dlm_timestamp = datetime(2021, 1, 1, tzinfo=timezone.utc)
        self.result.timestamp_osm = datetime.now(timezone.utc)

    def calculate(self) -> None:
        self.result.value = None  # TODO: do we want a result value
        self.result.description = Template(
            self.templates.result_description
        ).safe_substitute(
            {
                "attribute": f"'{self.attribute.capitalize()}'"
                if self.attribute is not None
                else _("'All attributes'"),
                "percent": format_percent(
                    1 - (self.matched_data.not_matched / self.matched_data.total_dlm),
                    format="##0.#%",
                    locale=get_locale(),
                ),
            }
        )

    def create_figure(self) -> None:
        if self.matched_data.total_dlm == 0:
            return
        fig = make_subplots(
            rows=1,
            cols=2,
        )

        fig.add_trace(plot_presence(self.matched_data), row=1, col=1)

        # TODO: create plot if both is 0
        if self.matched_data.both > 0:
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

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


def plot_presence(result: MatchedData) -> pgo.Bar:
    labels = [_("Both"), _("Only DLM"), _("Only OSM"), _("Missing both")]
    values = [result.both, result.only_dlm, result.only_osm, result.missing_both]
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
    values = [result.present_in_both_agree, result.present_in_both_not_agree]
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
