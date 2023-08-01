import logging
from string import Template

import plotly.graph_objects as pgo
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from geojson import Feature
from plotly.subplots import make_subplots

from ohsome_quality_analyst.indicators.base import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.topics.models import BaseTopic as Topic


class Currentness(BaseIndicator):
    """
    Ratio of all contributions that have been edited since 2008 until the
    current day in relation with years without mapping activities in the same
    time range

    Attributes:
        t4 (int): Number of years it should have been since 50%
            of the items were last edited to be in the second best class
        t3 (int): Number of years it should have been since 50%
            of the items were last edited to be in the second best class
        t2 (int): Number of years it should have been since 50%
            of the items were last edited to be in the third best class
        t1 (int): Number of years it should have been since 50%
            of the items were last edited to be in the second worst class. If
            the result is lower than this threshold, it is assigned to the worst class
    """

    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        # thresholds denote number of months (years) since today:
        self.months_green = 36  # 3 years
        self.months_yellow = 96  # 8 years
        self.t1 = 0.75
        self.t2 = 0.5
        self.t3 = 0.3
        self.interval = ""  # YYYY-MM-DD/YYYY-MM-DD/P1Y
        self.to_timestamps = []  # up to timestamp
        self.from_timestamps = []
        self.contrib_abs = []  # indices denote years since latest timestamp
        self.contrib_rel = []  # "
        self.contrib_sum = 0

        self.threshold_low_contributions = 25

    async def preprocess(self):
        """Get absolute number of contributions for each year since given start date"""
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        end = latest_ohsome_stamp.strftime("%Y-%m-%d")
        start = "2008-" + latest_ohsome_stamp.strftime("%m-%d")
        self.interval = "{}/{}/{}".format(start, end, "P1M")
        # Fetch all contributions of in yearly buckets since 2008
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            time=self.interval,
            count_latest_contributions=True,
            contribution_type="geometryChange,creation,tagChange",  # exclude 'deletion'
        )
        for c in reversed(response["result"]):  # latest contributions first
            self.to_timestamps.append(isoparse(c["toTimestamp"]))
            self.from_timestamps.append(isoparse(c["fromTimestamp"]))
            self.timestamps = [
                fr + (to - fr) / 2
                for to, fr in zip(self.to_timestamps, self.from_timestamps)
            ]
            self.contrib_abs.append(c["value"])
            self.contrib_sum += c["value"]
        self.result.timestamp_osm = self.to_timestamps[0]

    def calculate(self):
        """Calculate the years since over 50% of the elements were last edited"""
        logging.info("Calculation for indicator: {}".format(self.metadata.name))

        if self.contrib_sum == 0:
            self.result.description = (
                "In the area of interest no features of "
                "the selected topic are present today."
            )
            return

        self.contrib_rel = [c / self.contrib_sum for c in self.contrib_abs]

        self.contrib_rel_red = self.contrib_rel[self.months_yellow :]
        self.contrib_abs_red = self.contrib_abs[self.months_yellow :]
        self.to_timestamps_red = self.to_timestamps[self.months_yellow :]
        self.from_timestamps_red = self.from_timestamps[self.months_yellow :]
        self.timestamps_red = [
            fr + (to - fr) / 2
            for to, fr in zip(self.to_timestamps_red, self.from_timestamps_red)
        ]

        self.contrib_rel_yellow = self.contrib_rel[
            self.months_green : self.months_yellow
        ]
        self.contrib_abs_yellow = self.contrib_abs[
            self.months_green : self.months_yellow
        ]
        self.to_timestamps_yellow = self.to_timestamps[
            self.months_green : self.months_yellow
        ]
        self.from_timestamps_yellow = self.from_timestamps[
            self.months_green : self.months_yellow
        ]
        self.timestamps_yellow = [
            fr + (to - fr) / 2
            for to, fr in zip(self.to_timestamps_yellow, self.from_timestamps_yellow)
        ]

        self.contrib_rel_green = self.contrib_rel[0 : self.months_green]
        self.contrib_abs_green = self.contrib_abs[0 : self.months_green]
        self.to_timestamps_green = self.to_timestamps[0 : self.months_green]
        self.from_timestamps_green = self.from_timestamps[0 : self.months_green]
        self.timestamps_green = [
            fr + (to - fr) / 2
            for to, fr in zip(self.to_timestamps_green, self.from_timestamps_green)
        ]

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
        elif sum(self.contrib_rel_green) >= self.t1:
            self.result.class_ = 5
            label = "green"
        elif sum(self.contrib_rel_green) >= self.t2:
            self.result.class_ = 4
            label = "green"
        elif sum(self.contrib_rel_red) >= self.t3:
            self.result.class_ = 1
            label = "red"
        elif sum(self.contrib_rel_green) + sum(self.contrib_rel_yellow) >= self.t1:
            self.result.class_ = 3
            label = "yellow"
        elif (
            sum(self.contrib_rel_green) + sum(self.contrib_rel_yellow) < self.t1
            and sum(self.contrib_rel_red) < self.t3
        ):
            self.result.class_ = 2
            label = "yellow"
        else:
            raise ValueError("Ratio has an unexpected value.")

        if self.contrib_sum < self.threshold_low_contributions:
            label_description = (
                f"Attention: There are only {self.contrib_sum} "
                f" with the selected filter in this region."
                f" The significance of the result is limited.",
            )
        else:
            label_description = self.metadata.label_description[label]
        self.result.description = Template(self.metadata.result_description).substitute(
            contrib_rel_t2=f"{sum(self.contrib_rel_green)*100:.2f}",
            topic=self.topic.name,
            from_timestamp=self.from_timestamps[0 : self.months_green][-1].strftime(
                "%m/%d/%Y"
            ),
            to_timestamp=self.to_timestamps[0].strftime("%m/%d/%Y"),
            elements=int(self.contrib_sum),
            label_description=label_description,
            from_timestamp_50_perc=(
                self.to_timestamps[0]
                - relativedelta(months=get_median_month(self.contrib_rel))
            ).strftime("%m/%d/%Y"),
            to_timestamp_50_perc=self.to_timestamps[0].strftime("%m/%d/%Y"),
        )

        last_edited_year = get_how_many_years_no_activity(self.contrib_abs)
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
                "contrib_rel": self.contrib_rel_green,
                "contrib_abs": self.contrib_abs_green,
                "to_timestamps": self.to_timestamps_green,
                "from_timestamps": self.from_timestamps_green,
                "timestamps": self.timestamps_green,
            },
            "yellow": {
                "color": "yellow",
                "contrib_rel": self.contrib_rel_yellow,
                "contrib_abs": self.contrib_abs_yellow,
                "to_timestamps": self.to_timestamps_yellow,
                "from_timestamps": self.from_timestamps_yellow,
                "timestamps": self.timestamps_yellow,
            },
            "red": {
                "color": "red",
                "contrib_abs": self.contrib_abs_red,
                "contrib_rel": self.contrib_rel_red,
                "to_timestamps": self.to_timestamps_red,
                "from_timestamps": self.from_timestamps_red,
                "timestamps": self.timestamps_red,
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
