import json
from dataclasses import dataclass
from pathlib import Path
from string import Template

import plotly.graph_objects as pgo
from geojson import Feature
from ohsome_filter_to_sql.main import ohsome_filter_to_sql

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic as Topic


@dataclass
class Bin:
    """Bin or bucket of contributions.

    Indices denote years since latest timestamp.
    """

    contrib_abs: list
    to_timestamps: list
    from_timestamps: list
    timestamps: list  # middle of time period


class UserActivity(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.bin_total = None

    async def preprocess(self) -> None:
        where = ohsome_filter_to_sql(self.topic.filter)
        with open(Path(__file__).parent / "query.sql", "r") as file:
            template = file.read()
        query = Template(template).substitute(
            {
                "aoi": json.dumps(self.feature["geometry"]),
                "filter": where,
                "contributions_table": get_config_value("ohsomedb_contributions_table"),
            }
        )
        results = await client.fetch(query, database="ohsomedb")
        if len(results) == 0:
            return
        to_timestamps = []
        from_timestamps = []
        timestamps = []
        contrib_abs = []
        for r in reversed(results):  # latest contributions first
            to_timestamps.append(r[0])
            from_timestamps.append(r[0])
            timestamps.append(r[0])
            contrib_abs.append(r[1])
        self.bin_total = Bin(
            contrib_abs,
            to_timestamps,
            from_timestamps,
            timestamps,
        )
        self.result.timestamp_osm = self.bin_total.to_timestamps[0]

    def calculate(self):
        contrib_sum = sum(self.bin_total.contrib_abs)
        edge_cases = check_major_edge_cases(contrib_sum)
        if edge_cases:
            self.result.description = edge_cases
            return
        self.result.description = check_minor_edge_cases(
            contrib_sum,
            self.bin_total,
        )

    def create_figure(self):
        fig = pgo.Figure()

        bucket = self.bin_total

        customdata = list(
            zip(
                bucket.contrib_abs,
                [ts.strftime("%d %b %Y") for ts in bucket.to_timestamps],
                [ts.strftime("%d %b %Y") for ts in bucket.from_timestamps],
            )
        )

        hovertemplate = (
            "%{y} Users "
            "were modifying in the period from "
            "%{customdata[2]} to %{customdata[1]}"
            "<extra></extra>"
        )

        fig.add_trace(
            pgo.Bar(
                name="Features [%]",
                x=bucket.timestamps,
                y=bucket.contrib_abs,
                marker_color="steelblue",
                customdata=customdata,
                hovertemplate=hovertemplate,
            )
        )

        fig.update_layout(
            title_text="User Activity",
            legend=dict(
                x=0.02,
                y=0.95,
                bgcolor="rgba(255,255,255,0.66)",
            ),
        )

        fig.update_xaxes(
            title_text="Date",
            ticklabelmode="period",
            minor=dict(
                ticks="inside",
                dtick="M1",
                tickcolor="rgba(128,128,128,0.66)",
            ),
            tickformat="%b %Y",
            ticks="outside",
            tick0=bucket.to_timestamps[-1],
        )

        fig.update_yaxes(
            title_text="Active Users [#]",
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


def check_major_edge_cases(contrib_sum) -> str:
    """Check edge cases and return description.

    Major edge cases should lead to cancellation of calculation.
    """
    if contrib_sum == 0:  # no data
        return (
            "In the area of interest no features of the selected topic are present "
            "today."
        )
    else:
        return ""


def check_minor_edge_cases(contrib_sum, bin_total) -> str:
    """Check edge cases and return description.

    Minor edge cases should *not* lead to cancellation of calculation.
    """
    num_months = get_num_months_last_contrib(bin_total.contrib_abs)
    if contrib_sum < 25:  # not enough data
        return (
            "Please note that in the area of interest less than 25 features of the "
            "selected topic are present today. "
        )
    elif num_months >= 12:
        return (
            f"Please note that there was no mapping activity for {num_months} months "
            "in this region. "
        )
    else:
        return ""


def get_num_months_last_contrib(contrib: list) -> int:
    """Get the number of months since today when the last contribution has been made."""
    for month, contrib in enumerate(contrib):  # latest contribution first
        if contrib != 0:
            return month


def get_median_month(contrib_rel: list) -> int:
    """Get the number of months since today when 50% of contributions have been made."""
    contrib_rel_cum = 0
    for month, contrib in enumerate(contrib_rel):  # latest contribution first
        contrib_rel_cum += contrib
        if contrib_rel_cum >= 0.5:
            return month
