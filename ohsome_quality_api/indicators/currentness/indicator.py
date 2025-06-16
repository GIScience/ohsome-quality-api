"""Currentness Indicator

Abbreviations:
    contrib_rel: Relative number of contributions per month [%]
    contrib_abs: Absolute number of contributions per month [%]
    contrib_sum: Total number of contributions
    ts: Timestamp
    th: Threshold
"""

import locale
import logging
import os
from dataclasses import dataclass
from string import Template

import plotly.graph_objects as pgo
import yaml
from dateutil.parser import isoparse
from geojson import Feature
from plotly.subplots import make_subplots

from ohsome_quality_api.definitions import Color
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic as Topic

# set locale for datetime to string formatting
try:
    locale.setlocale(locale.LC_ALL, ["en_US", locale.getencoding()])
except locale.Error:
    logging.warn(
        "Could not set locale to en_US. Output may be different than expected."
    )


@dataclass
class Bin:
    """Bin or bucket of contributions.

    Indices denote years since latest timestamp.
    """

    contrib_abs: list
    contrib_rel: list
    to_timestamps: list
    from_timestamps: list
    timestamps: list  # middle of time period


class Currentness(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        # thresholds for binning in months
        self.up_to_date, self.out_of_date, self.th_source = load_thresholds(
            self.topic.key
        )
        # thresholds for determining result class based on share of features in bins
        self.th1 = 0.75  # [%]
        self.th2 = 0.5
        self.th3 = 0.3
        self.contrib_sum = 0
        self.bin_total: Bin
        self.bin_up_to_date: Bin
        self.bin_in_between: Bin
        self.bin_out_of_date: Bin

    async def preprocess(self):
        """Fetch all latest contributions in monthly buckets since 2008

        Beside the creation, latest contribution includes also the change to the
        geometry and the tag. It excludes deletion.
        """
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        end = latest_ohsome_stamp.strftime("%Y-%m-%d")
        start = "2008-" + latest_ohsome_stamp.strftime("%m-%d")
        interval = "{}/{}/{}".format(start, end, "P1M")  # YYYY-MM-DD/YYYY-MM-DD/P1Y
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            time=interval,
            count_latest_contributions=True,
            contribution_type="geometryChange,creation,tagChange",  # exclude 'deletion'
        )
        to_timestamps = []
        from_timestamps = []
        timestamps = []
        contrib_abs = []
        contrib_sum = 0
        for c in reversed(response["result"]):  # latest contributions first
            to_ts = isoparse(c["toTimestamp"])
            from_ts = isoparse(c["fromTimestamp"])
            ts = from_ts + (to_ts - from_ts) / 2
            to_timestamps.append(to_ts)
            from_timestamps.append(from_ts)
            timestamps.append(ts)
            contrib_abs.append(c["value"])
            contrib_sum += c["value"]
        if contrib_sum == 0:
            contrib_rel = [0 for _ in contrib_abs]
        else:
            contrib_rel = [c / contrib_sum for c in contrib_abs]
        self.bin_total = Bin(
            contrib_abs,
            contrib_rel,
            to_timestamps,
            from_timestamps,
            timestamps,
        )
        self.contrib_sum = contrib_sum
        self.result.timestamp_osm = self.bin_total.to_timestamps[0]

    def calculate(self):
        """Determine up-to-date, in-between and out-of-date contributions.

        Put contributions into three bins: (1) up-to-date (2) in-between and (3)
        out-of-date. The range of those bins are based on the topic.
        After binning determine the result class based on share of features in each bin.
        """
        edge_cases = check_major_edge_cases(self.contrib_sum)
        if edge_cases:
            self.result.description = edge_cases
            return
        self.result.description = check_minor_edge_cases(
            self.contrib_sum,
            self.bin_total,
        )

        self.bin_up_to_date = create_bin(
            self.bin_total,
            0,
            self.up_to_date,
        )
        self.bin_in_between = create_bin(
            self.bin_total,
            self.up_to_date,
            self.out_of_date,
        )
        self.bin_out_of_date = create_bin(
            self.bin_total,
            self.out_of_date,
            len(self.bin_total.timestamps),
        )

        self.result.value = sum(self.bin_up_to_date.contrib_rel)

        if sum(self.bin_out_of_date.contrib_rel) >= self.th3:
            self.result.class_ = 1
        elif sum(self.bin_up_to_date.contrib_rel) >= self.th1:
            self.result.class_ = 5
        elif sum(self.bin_up_to_date.contrib_rel) >= self.th2:
            self.result.class_ = 4
        elif (
            sum(self.bin_up_to_date.contrib_rel) + sum(self.bin_in_between.contrib_rel)
            >= self.th1
        ):
            self.result.class_ = 3
        elif (
            sum(self.bin_up_to_date.contrib_rel) + sum(self.bin_in_between.contrib_rel)
            >= self.th2
        ):
            self.result.class_ = 2
        else:
            self.result.class_ = 1

        label_description = self.templates.label_description[self.result.label]
        self.result.description += Template(
            self.templates.result_description
        ).substitute(
            up_to_date_contrib_rel=f"{sum(self.bin_up_to_date.contrib_rel) * 100:.0f}",
            num_of_elements=int(self.contrib_sum),
            from_timestamp=self.bin_up_to_date.from_timestamps[-1].strftime("%d %b %Y"),
            to_timestamp=self.bin_total.to_timestamps[0].strftime("%d %b %Y"),
        )
        self.result.description += "\n" + label_description

    def create_figure(self):
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for bucket, color in zip(
            (self.bin_up_to_date, self.bin_in_between, self.bin_out_of_date),
            (Color.GREEN, Color.YELLOW, Color.RED),
        ):
            customdata = list(
                zip(
                    bucket.contrib_abs,
                    [ts.strftime("%d %b %Y") for ts in bucket.to_timestamps],
                    [ts.strftime("%d %b %Y") for ts in bucket.from_timestamps],
                )
            )
            hovertemplate = (
                "%{y} of features (%{customdata[0]}) "
                "were last modified in the period from "
                "%{customdata[2]} to %{customdata[1]}"
                "<extra></extra>"
            )

            # trace for relative contributions
            fig.add_trace(
                pgo.Bar(
                    name="{:.1%} {}".format(
                        sum(bucket.contrib_rel),
                        self.get_threshold_text(color),
                    ),
                    x=bucket.timestamps,
                    y=bucket.contrib_rel,
                    marker_color=color.value,
                    customdata=customdata,
                    hovertemplate=hovertemplate,
                )
            )

            # mock trace for absolute contributions to get second y-axis
            fig.add_trace(
                pgo.Bar(
                    name=None,
                    x=bucket.timestamps,
                    y=bucket.contrib_abs,
                    marker_color=color.value,
                    showlegend=False,
                    hovertemplate=None,
                    hoverinfo="skip",
                ),
                secondary_y=True,
            )

        fig.update_layout(
            title_text=("Currentness"),
        )
        fig.update_xaxes(
            title_text="Date of Last Edit",
            ticklabelmode="period",
            minor=dict(
                ticks="inside",
                dtick="M1",
                tickcolor="rgba(128,128,128,0.66)",
            ),
            tickformat="%b %Y",
            ticks="outside",
            tick0=self.bin_total.to_timestamps[-1],
        )
        fig.update_yaxes(
            title_text="Features [%]",
            tickformatstops=[
                dict(dtickrange=[None, 0.001], value=".2%"),
                dict(dtickrange=[0.001, 0.01], value=".1%"),
                dict(dtickrange=[0.01, 0.1], value=".0%"),
                dict(dtickrange=[0.1, None], value=".0%"),
            ],
            secondary_y=False,
        )
        fig.update_yaxes(
            title_text="Features [#]",
            tickformat=".",
            secondary_y=True,
            griddash="dash",
        )
        # fixed legend, because we do not expect high contributions in 2008
        fig.update_legends(
            title="Last Edit to a Feature{}".format(self.get_source_text()),
            x=0.02,
            y=0.95,
            bgcolor="rgba(255,255,255,0.66)",
        )

        fig.add_layout_image(
            dict(
                source="https://media.licdn.com/dms/image/v2/D560BAQE9rkvB7vB_cg/company-logo_200_200/company-logo_200_200/0/1711546373172/heigit_logo?e=2147483647&v=beta&t=pWdgVEOkz7VBhH2WbM5_DJeTs7RsdVXbolKU3ftS1iY",
                xref="paper",
                yref="paper",
                x=0.759,
                y=1,
                sizex=0.3,
                sizey=0.3,
                sizing="contain",
                opacity=0.3,
                layer="above",
            )
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
        fig.show()

    def get_threshold_text(self, color: Color) -> str:
        up_to_date_str = month_to_year_month(self.up_to_date)
        out_of_date_str = month_to_year_month(self.out_of_date)
        match color:
            case color.GREEN:
                return f"younger than {up_to_date_str}"
            case color.YELLOW:
                return f"between {up_to_date_str} and {out_of_date_str}"
            case color.RED:
                return f"older than {out_of_date_str}"
            case _:
                raise ValueError()

    def get_source_text(self) -> str:
        if self.th_source != "":
            self.th_source = f"<a href='{self.th_source}' target='_blank'>*</a>"
        return self.th_source


def month_to_year_month(months: int):
    years, months = divmod(months, 12)
    years_str = months_str = ""
    if years != 0:
        years_str = f"{years} year" + ("s" if years > 1 else "")
    if months != 0:
        months_str = f"{months} month" + ("s" if months > 1 else "")
    return " ".join([years_str, months_str]).strip()


def load_thresholds(topic_key: str) -> tuple[int, int, str]:
    """Load thresholds based on topic keys.

    Thresholds denote the number of months since today.
    Thresholds are used to discern if the features are up-to-date or out-of-date.

    up-to-data: everything up to this number of months is considered up-to-date
    out-of-date: everything older than this number of months is considered out-of-date

    Returns:
        tuple: (up-to-date, out-of-date)
    """
    file = os.path.join(os.path.dirname(__file__), "thresholds.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    try:
        # topic thresholds
        source = raw[topic_key].get("source", "")
        thresholds = raw[topic_key]["thresholds"]
        up_to_date, out_of_date = (thresholds["up_to_date"], thresholds["out_of_date"])
    except KeyError:
        # default thresholds
        return 36, 96, ""
    return up_to_date, out_of_date, source


def create_bin(b: Bin, i: int, j: int) -> Bin:
    return Bin(
        contrib_abs=b.contrib_abs[i:j],
        contrib_rel=b.contrib_rel[i:j],
        to_timestamps=b.to_timestamps[i:j],
        from_timestamps=b.from_timestamps[i:j],
        timestamps=b.timestamps[i:j],
    )


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
