import logging
from dataclasses import dataclass
from statistics import median
from string import Template

import numpy as np
import plotly.graph_objects as pgo
from babel.dates import format_date
from fastapi_i18n import _, get_locale
from geojson import Feature

from ohsome_quality_api import ohsomedb
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import Topic

logger = logging.getLogger(__name__)


@dataclass
class Bin:
    """Bin or bucket of users.

    Indices denote years since latest timestamp.
    """

    users_abs: list
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
        results = await ohsomedb.users(
            bpolys=self.feature.geometry,
            filter_=self.topic.filter,
        )
        if len(results) == 0:
            return
        timestamps = []
        users_abs = []
        for r in reversed(results):
            timestamps.append(r[0])
            users_abs.append(r[1])
        self.bin_total = Bin(
            users_abs,
            timestamps,
        )
        self.result.timestamp_osm = timestamps[0]

    def calculate(self):
        edge_cases = check_major_edge_cases(sum(self.bin_total.users_abs))
        if edge_cases:
            self.result.description = edge_cases
            return
        else:
            self.result.description = ""
        self.result.value = int(median(self.bin_total.users_abs[1:37]))
        label_description = getattr(self.templates.label_description, self.result.label)
        self.result.description += Template(
            self.templates.result_description
        ).substitute(
            median_users=self.result.value,
            from_timestamp=format_date(
                self.bin_total.timestamps[37],
                format="MMM yyyy",
                locale=get_locale(),
            ),
            to_timestamp=format_date(
                self.bin_total.timestamps[1],
                format="MMM yyyy",
                locale=get_locale(),
            ),
        )
        self.result.description += "\n" + label_description

    def create_figure(self):
        if check_major_edge_cases(sum(self.bin_total.users_abs)):
            logger.info("No user activity. Skipping figure creation.")
            return
        fig = pgo.Figure()
        bucket = self.bin_total

        values = bucket.users_abs
        timestamps = bucket.timestamps

        window = 12
        weights = np.arange(1, window + 1)
        weighted_avg = []

        values_for_mean = values[1:]
        for i in range(len(values_for_mean) + 1):
            if i == 0:
                weighted_avg.append(None)
                continue
            start = max(1, i - window + 1)
            window_vals = values_for_mean[start : i + 1]
            window_weights = weights[-len(window_vals) :]
            avg = np.dot(window_vals, window_weights) / window_weights.sum()
            weighted_avg.append(avg)

        # regression trend line for the last 36 months
        if len(weighted_avg) >= 36:
            x = np.arange(len(weighted_avg))
            x_last = x[1:37]
            y_last = np.array(weighted_avg[1:37])

            coeffs = np.polyfit(x_last, y_last, 1)
            trend_y = np.polyval(coeffs, x_last)
            trend_timestamps = timestamps[1:37]
        else:
            trend_timestamps = []
            trend_y = []

        customdata = list(
            zip(
                bucket.users_abs,
                [
                    format_date(ts, format="MMM yyyy", locale=get_locale())
                    for ts in bucket.timestamps
                ],
            )
        )

        hovertemplate = _(
            "%{y} Users were modifying in %{customdata[1]}<extra></extra>"
        )

        fig.add_trace(
            pgo.Bar(
                name=_("Users per Month"),
                x=timestamps,
                y=values,
                marker_color="lightgrey",
                customdata=customdata,
                hovertemplate=hovertemplate,
            )
        )

        fig.add_trace(
            pgo.Scatter(
                name=_("12-Month Weighted Avg"),
                x=timestamps,
                y=weighted_avg,
                mode="lines",
                line=dict(color="steelblue", width=3),
                hovertemplate=_("Weighted Avg: %{y:.0f} Users<extra></extra>"),
            )
        )

        if len(trend_timestamps) > 0:
            fig.add_trace(
                pgo.Scatter(
                    name=_("Last 36M Trend"),
                    x=trend_timestamps,
                    y=trend_y,
                    mode="lines",
                    line=dict(color="red", width=4, dash="dash"),
                    hovertemplate=_("Trend: %{y:.0f} Users<extra></extra>"),
                )
            )

        fig.update_layout(
            title=dict(
                text=_("User Activity"),
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
            title_text=_("Date"),
            ticklabelmode="period",
            minor=dict(
                ticks="inside",
                dtick="M1",
                tickcolor="rgba(128,128,128,0.66)",
            ),
            tickformat="%b %Y",
            ticks="outside",
            tick0=bucket.timestamps[-1],
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)",
        )

        fig.update_yaxes(
            title_text=_("Active Users [#]"),
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
        return _("In this region no user activity was recorded. ")
    else:
        return ""
