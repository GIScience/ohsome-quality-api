"""Currentness Indicator

Abbreviations:
    contrib_rel: Relative number of contributions per month [%]
    contrib_abs: Absolute number of contributions per month [%]
    contrib_sum: Total number of contributions
    ts: Timestamp
    th: Threshold
"""

import logging
import os
from dataclasses import dataclass
from string import Template

import plotly.graph_objects as pgo
import yaml
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from geojson import Feature
from plotly.subplots import make_subplots

from ohsome_quality_analyst.indicators.base import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.topics.models import BaseTopic as Topic


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
        self.up_to_date, self.out_of_date = load_thresholds(self.topic.key)
        # thresholds for determining result class based on share of features in bins
        self.th1 = 0.75  # [%]
        self.th2 = 0.5
        self.th3 = 0.3
        self.interval = ""  # YYYY-MM-DD/YYYY-MM-DD/P1Y
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
        self.interval = "{}/{}/{}".format(start, end, "P1M")
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            time=self.interval,
            count_latest_contributions=True,
            contribution_type="geometryChange,creation,tagChange",  # exclude 'deletion'
        )
        to_timestamps = []
        from_timestamps = []
        timestamps = []
        contrib_abs = []
        contrib_rel = []
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
        """Determine up-to-date and out-of-date contributions.

        Put contributions into three bins: (1) up to date (2) in between and (3) out of
        date. The range of those bins are based on the topic. After binning determine
        the result class based on share of features in each bin.
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

        label_description = self.metadata.label_description[self.result.label]
        self.result.description += Template(
            self.metadata.result_description
        ).substitute(
            contrib_rel_t2=f"{sum(self.bin_up_to_date.contrib_rel) * 100:.2f}",
            topic=self.topic.name,
            from_timestamp=self.bin_up_to_date.from_timestamps[-1].strftime("%m/%d/%Y"),
            to_timestamp=self.bin_total.to_timestamps[0].strftime("%m/%d/%Y"),
            elements=int(self.contrib_sum),
            from_timestamp_50_perc=(
                self.bin_total.to_timestamps[0]
                - relativedelta(months=get_median_month(self.bin_total.contrib_rel))
            ).strftime("%m/%d/%Y"),
            to_timestamp_50_perc=self.bin_total.to_timestamps[0].strftime("%m/%d/%Y"),
        )
        self.result.description += label_description

    def create_figure(self):
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for bucket, color in zip(
            (self.bin_up_to_date, self.bin_in_between, self.bin_out_of_date),
            ("green", "yellow", "red"),
        ):
            customdata = list(
                zip(
                    bucket.contrib_abs,
                    [ts.strftime("%m/%d/%Y") for ts in bucket.to_timestamps],
                    [ts.strftime("%m/%d/%Y") for ts in bucket.from_timestamps],
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
                    name="{:.0%}".format(sum(bucket.contrib_rel)),
                    x=bucket.timestamps,
                    y=bucket.contrib_rel,
                    marker_color=color,
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
                    marker_color=color,
                    showlegend=False,
                    hovertemplate=None,
                    hoverinfo="skip",
                ),
                secondary_y=True,
            )

        fig.update_layout(
            title_text="Currentness",
            legend_title_text="Share of up-to-date features",
        )
        fig.update_xaxes(
            title_text="Interval: {}".format(self.interval),
            ticklabelmode="period",
            tickformat="%b\n%Y",
            tick0=self.bin_total.to_timestamps[-1],
        )
        fig.update_yaxes(
            title_text="Percentage of Latest Contributions",
            tickformat=".0%",
        )
        fig.update_yaxes(
            title_text="Absolute Number of Latest Contributions",
            tickformat=".",
            secondary_y=True,
        )
        # fixed legend, because we do not expect high contributions in 2008
        fig.update_legends(
            x=0,
            y=0.95,
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


def load_thresholds(topic_key: str) -> tuple[int, int]:
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
        thresholds = raw[topic_key]["thresholds"]
        return (thresholds["up_to_date"], thresholds["out_of_date"])
    except KeyError:
        # default thresholds
        return (36, 96)


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
            "Attention: In the area of interest less than 25 features of the"
            " selected topic are present today. The significance of the result is"
            " low."
        )
    elif num_months >= 12:
        return (
            f"Attention: There was no mapping activity for {num_months} months in "
            f"this region."
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
