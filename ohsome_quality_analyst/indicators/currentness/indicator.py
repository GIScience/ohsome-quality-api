"""Currentness Indicator

Abbreviations:
    contrib_rel: Relative number of contributions per month [%]
    contrib_abs: Absolute number of contributions per month [%]
    contrib_sum: Total number of contributions
    ts: Timestamp
"""

import logging
from dataclasses import dataclass
from string import Template

import plotly.graph_objects as pgo
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from geojson import Feature
from plotly.subplots import make_subplots
from topics.definitions import load_topic_thresholds

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
    """
    Ratio of all contributions that have been edited since 2008 until the
    current day in relation with years without mapping activities in the same
    time range

    Attributes:
        t1, t2, t3 (float): Ratio of all contributions to be in a specific class
    """

    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        # everything up to this number of months is considered up-to-date:
        self.up_to_date = 36  # number of months since today
        # everything older then this number of months is considered out-of-date:
        self.out_of_date = 96  # number of months since today
        self.t1 = 0.75  # [%]
        self.t2 = 0.5
        self.t3 = 0.3
        self.interval = ""  # YYYY-MM-DD/YYYY-MM-DD/P1Y
        self.contrib_sum = 0
        self.bin_total: Bin
        self.bin_up_to_date: Bin
        self.bin_in_between: Bin
        self.bin_out_of_date: Bin

        self.threshold_low_contributions = 25

    async def preprocess(self):
        """Fetch all latest contributions in monthly buckets since 2008"""
        thresholds = load_topic_thresholds(
            indicator_name="currentness",
            topic_name=self.topic.key,
        )
        if thresholds is not None:
            self.up_to_date = thresholds[0]
            self.out_of_date = thresholds[1]

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
        for c in reversed(response["result"]):  # latest contributions first
            to_ts = isoparse(c["toTimestamp"])
            from_ts = isoparse(c["fromTimestamp"])
            ts = from_ts + (to_ts - from_ts) / 2
            to_timestamps.append(to_ts)
            from_timestamps.append(from_ts)
            timestamps.append(ts)
            contrib_abs.append(c["value"])
            self.contrib_sum += c["value"]
        contrib_rel = [c / self.contrib_sum for c in contrib_abs]
        self.bin_total = Bin(
            contrib_abs,
            contrib_rel,
            to_timestamps,
            from_timestamps,
            timestamps,
        )
        self.result.timestamp_osm = self.bin_total.to_timestamps[0]

    def calculate(self):
        """Calculate the years since over 50% of the elements were last edited"""
        if self.contrib_sum == 0:
            self.result.description = (
                "In the area of interest no features of "
                "the selected topic are present today."
            )
            return

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

        # TODO: is this tested?
        # TODO: factor out to a check_edge_cases function (see mapping saturation)
        if self.contrib_sum < self.threshold_low_contributions:
            self.result.description = (
                "In the area of interest less than {0}".format(
                    self.threshold_low_contributions
                )
                + " features of the selected topic are present today. "
                + "The significance of the result is low."
            )
            pass
        # If green above 50 -> green
        # if green + yellow above 50 -> yellow
        elif sum(self.bin_out_of_date.contrib_rel) >= self.t3:
            self.result.class_ = 1
        elif sum(self.bin_up_to_date.contrib_rel) >= self.t1:
            self.result.class_ = 5
        elif sum(self.bin_up_to_date.contrib_rel) >= self.t2:
            self.result.class_ = 4
        elif (
            sum(self.bin_up_to_date.contrib_rel) + sum(self.bin_in_between.contrib_rel)
            >= self.t1
        ):
            self.result.class_ = 3
        elif (
            sum(self.bin_up_to_date.contrib_rel) + sum(self.bin_in_between.contrib_rel)
            >= self.t2
        ):
            self.result.class_ = 2
        else:
            self.result.class_ = 1

        if self.contrib_sum < self.threshold_low_contributions:
            label_description = (
                f"Attention: There are only {self.contrib_sum} "
                f" with the selected filter in this region."
                f" The significance of the result is limited.",
            )
        else:
            label_description = self.metadata.label_description[self.result.label]
        self.result.description = Template(self.metadata.result_description).substitute(
            contrib_rel_t2=f"{sum(self.bin_up_to_date.contrib_rel) * 100:.2f}",
            topic=self.topic.name,
            from_timestamp=self.bin_up_to_date.from_timestamps[-1].strftime("%m/%d/%Y"),
            to_timestamp=self.bin_total.to_timestamps[0].strftime("%m/%d/%Y"),
            elements=int(self.contrib_sum),
            label_description=label_description,
            from_timestamp_50_perc=(
                self.bin_total.to_timestamps[0]
                - relativedelta(months=get_median_month(self.bin_total.contrib_rel))
            ).strftime("%m/%d/%Y"),
            to_timestamp_50_perc=self.bin_total.to_timestamps[0].strftime("%m/%d/%Y"),
        )

        last_edited_year = get_num_months_last_contrib(self.bin_total.contrib_abs)
        if last_edited_year > 0:
            self.result.description += (
                f" Attention: There was no mapping activity for "
                f"{last_edited_year} year(s) in this region."
            )

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
            )

            # Trace for relative contributions
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

            # Mock trace for absolute contributions to get second y-axis
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
            # hovermode="x",  : TODO
            title_text=("Currentness"),
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


def get_num_months_last_contrib(contrib: list) -> int:
    """Get the number of months since today when the last contribution has been made."""
    for month, contrib in enumerate(contrib):  # latest contribution first
        if contrib != 0:
            return month


def get_median_month(contrib_rel: list) -> int:
    """Get the number of years since today when 50% of contributions have been made."""
    contrib_rel_cum = 0
    for month, contrib in enumerate(contrib_rel):  # latest contribution first
        contrib_rel_cum += contrib
        if contrib_rel_cum >= 0.5:
            return month


def create_bin(b: Bin, i: int, j: int) -> Bin:
    return Bin(
        contrib_abs=b.contrib_abs[i:j],
        contrib_rel=b.contrib_rel[i:j],
        to_timestamps=b.to_timestamps[i:j],
        from_timestamps=b.from_timestamps[i:j],
        timestamps=b.timestamps[i:j],
    )
