import logging
from dataclasses import dataclass
from string import Template

import plotly.graph_objects as pgo
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from geojson import Feature
from plotly.subplots import make_subplots

# from topics.definitions import load_topic_thresholds
from ohsome_quality_analyst.indicators.base import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.topics.models import BaseTopic as Topic


@dataclass
class Bin:
    """Bucket of contributions.

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
        self.t1 = 0.75  # percentage
        self.t2 = 0.5  # percentage
        self.t3 = 0.3  # percentage
        self.interval = ""  # YYYY-MM-DD/YYYY-MM-DD/P1Y
        # self.to_timestamps = []
        # self.from_timestamps = []
        # self.timestamps = []  # middle of time period
        # self.contrib_abs = []  # indices denote years since latest timestamp
        # self.contrib_rel = []  # "
        self.contrib_sum = 0
        self.bin_total: Bin
        self.bin_up_to_date: Bin
        self.bin_in_between: Bin
        self.bin_ut_of_date: Bin

        self.threshold_low_contributions = 25

    async def preprocess(self):
        """Fetch all latest contributions in monthly buckets since 2008"""
        # thresholds = load_topic_thresholds(
        #     IndicatorName="currentness", TopicName=self.topic.key
        # )
        # if thresholds is not None:
        #     self.up_to_date = thresholds[0]
        #     self.out_of_date = thresholds[1]

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
        logging.info("Calculation for indicator: {}".format(self.metadata.name))

        if self.contrib_sum == 0:
            self.result.description = (
                "In the area of interest no features of "
                "the selected topic are present today."
            )
            return

        self.bin_out_of_date = self.create_bin(
            self.out_of_date,
            len(self.bin_total.timestamps),
        )
        # self.contrib_rel_outdated = self.contrib_rel[self.out_of_date :]
        # self.contrib_abs_outdated = self.contrib_abs[self.out_of_date :]
        # self.to_timestamps_outdated = self.to_timestamps[self.out_of_date :]
        # self.from_timestamps_outdated = self.from_timestamps[self.out_of_date :]
        # self.timestamps_outdated = [
        #     fr + (to - fr) / 2
        #     for to, fr in zip(
        #         self.to_timestamps_outdated, self.from_timestamps_outdated
        #     )
        # ]

        self.bin_in_between = self.create_bin(self.up_to_date, self.out_of_date)
        # self.contrib_rel_partially_current = self.contrib_rel[
        #     self.up_to_date : self.out_of_date
        # ]
        # self.contrib_abs_partially_current = self.contrib_abs[
        #     self.up_to_date : self.out_of_date
        # ]
        # self.to_timestamps_partially_current = self.to_timestamps[
        #     self.up_to_date : self.out_of_date
        # ]
        # self.from_timestamps_partially_current = self.from_timestamps[
        #     self.up_to_date : self.out_of_date
        # ]
        # self.timestamps_partially_current = [
        #     fr + (to - fr) / 2
        #     for to, fr in zip(
        #         self.to_timestamps_partially_current,
        #         self.from_timestamps_partially_current,
        #     )
        # ]

        self.bin_up_to_date = self.create_bin(0, self.up_to_date)
        # self.contrib_rel_up_to_date = self.contrib_rel[0 : self.up_to_date]
        # self.contrib_abs_up_to_date = self.contrib_abs[0 : self.up_to_date]
        # self.to_timestamps_up_to_date = self.to_timestamps[0 : self.up_to_date]
        # self.from_timestamps_up_to_date = self.from_timestamps[0 : self.up_to_date]
        # self.timestamps_up_to_date = [
        #     fr + (to - fr) / 2
        #     for to, fr in zip(
        #         self.to_timestamps_up_to_date, self.from_timestamps_up_to_date
        #     )
        # ]

        self.result.value = sum(self.bin_up_to_date.contrib_rel)

        # TODO: is this tested?
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
            from_timestamp=self.bin_up_to_date.from_timestamps[0 : self.up_to_date][
                -1
            ].strftime("%m/%d/%Y"),
            to_timestamp=self.bin_total.to_timestamps[0].strftime("%m/%d/%Y"),
            elements=int(self.contrib_sum),
            label_description=label_description,
            from_timestamp_50_perc=(
                self.bin_total.to_timestamps[0]
                - relativedelta(months=get_median_month(self.bin_total.contrib_rel))
            ).strftime("%m/%d/%Y"),
            to_timestamp_50_perc=self.bin_total.to_timestamps[0].strftime("%m/%d/%Y"),
        )

        last_edited_year = get_how_many_years_no_activity(self.bin_total.contrib_abs)
        if last_edited_year > 0:
            self.result.description += (
                f" Attention: There was no mapping activity for "
                f"{last_edited_year} year(s) in this region."
            )

    def create_figure(self):
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        colors_dict = {
            "green": {
                "color": "green",
                "contrib_rel": self.contrib_rel_up_to_date,
                "contrib_abs": self.contrib_abs_up_to_date,
                "to_timestamps": self.to_timestamps_up_to_date,
                "from_timestamps": self.from_timestamps_up_to_date,
                "timestamps": self.timestamps_up_to_date,
            },
            "yellow": {
                "color": "yellow",
                "contrib_rel": self.contrib_rel_partially_current,
                "contrib_abs": self.contrib_abs_partially_current,
                "to_timestamps": self.to_timestamps_partially_current,
                "from_timestamps": self.from_timestamps_partially_current,
                "timestamps": self.timestamps_partially_current,
            },
            "red": {
                "color": "red",
                "contrib_abs": self.contrib_abs_outdated,
                "contrib_rel": self.contrib_rel_outdated,
                "to_timestamps": self.to_timestamps_outdated,
                "from_timestamps": self.from_timestamps_outdated,
                "timestamps": self.timestamps_outdated,
            },
        }
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Common variables for both traces
        hover_template_abs = None
        hover_template_rel = (
            "%{y} of features (%{customdata[0]})<br>"
            "were last modified in the period from %{customdata[2]}"
            " to %{customdata[1]}<extra></extra>"
        )

        for color, data in colors_dict.items():
            contribution_percentage = round(sum(data["contrib_rel"]) * 100, 2)
            name = str(contribution_percentage) + "%"
            timestamps = data["timestamps"]

            customdata = list(
                zip(
                    data["contrib_abs"],
                    [
                        timestamp.strftime("%m/%d/%Y")
                        for timestamp in data["to_timestamps"]
                    ],
                    [
                        timestamp.strftime("%m/%d/%Y")
                        for timestamp in data["from_timestamps"]
                    ],
                )
            )

            # Trace for absolute contributions
            fig.add_trace(
                pgo.Bar(
                    name=name,
                    x=timestamps,
                    y=data["contrib_abs"],
                    marker_color=color,
                    showlegend=False,
                    hovertemplate=hover_template_abs,
                    hoverinfo="skip",
                ),
                secondary_y=True,
            )

            # Trace for relative contributions
            fig.add_trace(
                pgo.Bar(
                    name=name,
                    x=timestamps,
                    y=data["contrib_rel"],
                    marker_color=color,
                    hovertemplate=hover_template_rel,
                    customdata=customdata,
                )
            )

        y_max = max(self.contrib_rel) * 1.05

        fig.update_layout(
            hovermode="x",
            yaxis_range=[0, y_max],
            showlegend=True,
            title_text=("Currentness"),
        )
        fig.update_xaxes(
            title_text="Interval: {}".format(self.interval),
            ticklabelmode="period",
            # dtick="M6",
            tickformat="%b\n%Y",
            # tickangle=0,
            tick0=self.to_timestamps[-1],
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
        # fixed legend, because we do not high contributions in 2008
        fig.update_legends(
            x=0,
            y=0.95,
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def create_bin(self, i, j) -> Bin:
        return Bin(
            contrib_abs=self.bin_total.contrib_abs[i:j],
            contrib_rel=self.bin_total.contrib_rel[i:j],
            to_timestamps=self.bin_total.to_timestamps[i:j],
            from_timestamps=self.bin_total.from_timestamps[i:j],
            timestamps=self.bin_total.timestamps[i:j],
        )


def get_how_many_years_no_activity(contributions: list) -> int:
    """Get the number of years since today when the last contribution has been made."""
    for year, contrib in enumerate(contributions):  # latest contribution first
        if contrib != 0:
            return year


def get_median_month(contributions_rel: list) -> int:
    """Get the number of years since today when 50% of contributions have been made."""
    contrib_rel_cum = 0
    for month, contrib in enumerate(contributions_rel):  # latest contribution first
        contrib_rel_cum += contrib
        if contrib_rel_cum >= 0.5:
            return month
