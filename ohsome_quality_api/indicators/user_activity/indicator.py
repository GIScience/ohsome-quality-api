import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from string import Template

import numpy as np
import plotly.graph_objects as pgo
from geojson import Feature
from ohsome_filter_to_sql.main import ohsome_filter_to_sql

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic as Topic


@dataclass
class Bin:
    """Bin or bucket of users.

    Indices denote years since latest timestamp.
    """

    users_abs: list
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
        users_abs = []
        for r in reversed(results):
            to_timestamps.append(r[0])
            from_timestamps.append(r[0])
            timestamps.append(r[0])
            users_abs.append(r[1])
        self.bin_total = Bin(
            users_abs,
            to_timestamps,
            from_timestamps,
            timestamps,
        )
        self.result.timestamp_osm = self.bin_total.to_timestamps[0]

    def calculate(self):
        edge_cases = check_major_edge_cases(sum(self.bin_total.users_abs))
        if edge_cases:
            self.result.description = edge_cases
            return
        else:
            self.result.description = ""
        label_description = self.templates.label_description[self.result.label]
        self.result.description += Template(
            self.templates.result_description
        ).substitute(
            median_users=f"{int(median(self.bin_total.users_abs))}",
            from_timestamp=self.bin_total.timestamps[-1].strftime("%b %Y"),
            to_timestamp=self.bin_total.timestamps[0].strftime("%b %Y"),
        )
        self.result.description += "\n" + label_description

    def create_figure(self):
        fig = pgo.Figure()
        bucket = self.bin_total

        values = bucket.users_abs
        timestamps = bucket.timestamps

        window = 12
        weights = np.arange(1, window + 1)
        weighted_avg = []

        for i in range(len(values)):
            start = max(0, i - window + 1)
            window_vals = values[start : i + 1]
            window_weights = weights[-len(window_vals) :]
            avg = np.dot(window_vals, window_weights) / window_weights.sum()
            weighted_avg.append(avg)

        # regression trend line for the last 36 months
        if len(values) >= 36:
            x = np.arange(len(values))
            x_last = x[:36]
            y_last = np.array(values[:36])

            coeffs = np.polyfit(x_last, y_last, 1)
            trend_y = np.polyval(coeffs, x_last)
            breakpoint()
            trend_timestamps = timestamps[:36]
        else:
            trend_timestamps = []
            trend_y = []

        customdata = list(
            zip(
                bucket.users_abs,
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
                name="Users per Month",
                x=timestamps,
                y=values,
                marker_color="lightgrey",
                customdata=customdata,
                hovertemplate=hovertemplate,
            )
        )

        fig.add_trace(
            pgo.Scatter(
                name="12-Month Weighted Avg",
                x=timestamps,
                y=weighted_avg,
                mode="lines",
                line=dict(color="steelblue", width=3),
                hovertemplate="Weighted Avg: %{y:.0f} Users<extra></extra>",
            )
        )

        if len(trend_timestamps) > 0:
            fig.add_trace(
                pgo.Scatter(
                    name="Last 36M Trend",
                    x=trend_timestamps,
                    y=trend_y,
                    mode="lines",
                    line=dict(color="red", width=4, dash="dash"),
                    hovertemplate="Trend: %{y:.0f} Users<extra></extra>",
                )
            )

        fig.update_layout(
            title=dict(
                text="User Activity",
                x=0.5,
                xanchor="center",
                font=dict(size=22),
            ),
            plot_bgcolor="white",
            legend=dict(
                x=0.02,
                y=0.95,
                bgcolor="rgba(255,255,255,0.66)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(l=60, r=30, t=60, b=60),
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
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
        )

        fig.update_yaxes(
            title_text="Active Users [#]",
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
            zeroline=False,
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


def check_major_edge_cases(users_sum) -> str:
    """Check edge cases and return description.

    Major edge cases should lead to cancellation of calculation.
    """
    if users_sum == 0:  # no data
        return "In this region no user activity was recorded. "
    else:
        return ""
