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

from ohsome_quality_api.definitions import Color
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import Topic

logger = logging.getLogger(__name__)

QUERIES_DIR = Path(__file__).parent / "queries"


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
            query = Path(QUERIES_DIR / f"{self.attribute}.sql").read_text()
        else:
            query = Path(QUERIES_DIR / "all_attributes.sql").read_text()
        response = await client.fetch(query, str(self.feature["geometry"]))
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
        self.timestamp_dlm = datetime(2021, 1, 1, tzinfo=timezone.utc)
        self.result.timestamp_osm = datetime.now(timezone.utc)

    def calculate(self) -> None:
        breakpoint()
        if self.matched_data is None:
            raise ValueError("Expected matched data to be present (not None).")
        if self.matched_data.total_dlm is None:
            self.result.description = "No data in the area of interest."
            return

        if self.matched_data.total_dlm > 0:
            percentage = format_percent(
                1 - (self.matched_data.not_matched / self.matched_data.total_dlm),
                format="##0.#%",
                locale=get_locale(),
            )
            description = _(
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
                    " There are no matched roads where the "
                    "selected attribute(s) are present in both datasets"
                )
        else:
            percentage = format_percent(0, locale=get_locale())
            description = ""

        if self.attribute is not None:
            attribute_text = (
                f"'{self.attribute.capitalize()}'"  # Is this already translated?
            )
        else:
            attribute_text = _("'All attributes'")
        raw = Template(self.templates.result_description)
        result_description = raw.safe_substitute(
            {
                "attribute": attribute_text,
                "percent": percentage,
            }
        )
        self.result.description = result_description + description

    def create_figure(self) -> None:
        # TODO: Why is there no legend if only left plot has been plotted.
        # TODO: Make sure there is always a legend!
        if self.matched_data is None:
            raise ValueError("Expected matched data to be present (not None).")
        if self.matched_data.total_dlm is None or self.matched_data.total_dlm == 0:
            return

        fig = make_subplots(
            rows=1,
            cols=2,
        )

        fig.add_trace(
            plot_presence(self.matched_data, self.attribute),
            row=1,
            col=1,
        )

        # TODO: create plot if both is 0
        if self.matched_data.present_in_both > 0:
            fig.add_trace(
                plot_value_comparison(self.matched_data, self.attribute),
                row=1,
                col=2,
            )

        fig.update_layout(
            {
                "annotations": [
                    {
                        "text": (
                            f"<span style='font-size:smaller'>"
                            f"{_('DLM data from')} "
                            f"{self.timestamp_dlm.strftime('%Y')}"
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
        fig.update_yaxes(rangemode="nonnegative", title_text=_("Length (in km)"))
        fig.update_xaxes(rangemode="nonnegative")

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


def plot_presence(result: MatchedData, attribute: str | None) -> pgo.Bar:
    if attribute is None:
        labels = [
            _("Attributes are present in both"),
            _("Attributes are present only in DLM"),
            _("Attributes are present only in OSM"),
            _("Attributes are missing both"),
        ]
    else:
        labels = [
            _("Attribute is present in both"),
            _("Attribute is present only in DLM"),
            _("Attribute is present only in OSM"),
            _("Attribute is missing both"),
        ]
    values = [
        round(result.present_in_both, 2),
        round(result.only_dlm, 2),
        round(result.only_osm, 2),
        round(result.missing_both, 2),
    ]
    total = sum(values)
    text = []
    for value in values:
        value_formatted = format_percent(
            value / total,
            format="##0.#%",
            locale=get_locale(),
        )
        text.append(f"{value} ({value_formatted})")
    bar = pgo.Bar(
        x=labels,
        y=values,
        text=text,
        textposition="auto",
        marker_color=Color.BLUE.value,
        name=_("Attribute Presence [# (%)]"),
    )
    return bar


def plot_value_comparison(result: MatchedData, attribute: str | None) -> pgo.Bar:
    if attribute is None:
        labels = [
            _("Attributes are the same"),
            _("Attributes are different"),
        ]
    else:
        labels = [
            _("Attribute is the same"),
            _("Attribute is different"),
        ]
    values = [
        round(result.present_in_both_agree, 2),
        round(result.present_in_both_not_agree, 2),
    ]
    total = sum(values)
    text = []
    if total > 0:
        for value in values:
            value_formatted = format_percent(
                value / total,
                format="##0.#%",
                locale=get_locale(),
            )
            text.append(f"{value} ({value_formatted})")
    bar = pgo.Bar(
        x=labels,
        y=values,
        text=text,
        textposition="auto",
        marker_color=Color.PURPLE.value,
        name=_("Attribute Alignment [# (%)]"),
    )
    return bar
