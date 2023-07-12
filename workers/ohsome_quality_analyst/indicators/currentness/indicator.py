import logging
from string import Template

import plotly.graph_objects as pgo
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from geojson import Feature

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
        # thresholds denote number of years since today:
        self.t4 = 2
        self.t3 = 3
        self.t2 = 4
        self.t1 = 8
        self.interval = ""  # YYYY-MM-DD/YYYY-MM-DD/P1Y
        self.timestamps = []  # up to timestamp
        self.contrib_abs = []  # indices denote years since latest timestamp
        self.contrib_rel = []  # "
        self.contrib_sum = 0
        self.threshold_low_contributions = 25

    async def preprocess(self):
        """Get absolute number of contributions for each year since given start date"""
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        end = latest_ohsome_stamp.strftime("%Y-%m-%d")
        start = "2008-" + latest_ohsome_stamp.strftime("%m-%d")
        self.interval = "{}/{}/{}".format(start, end, "P1Y")
        # Fetch all contributions of in yearly buckets since 2008
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            time=self.interval,
            count_latest_contributions=True,
            contribution_type="geometryChange,creation,tagChange",  # exclude 'deletion'
        )
        for c in reversed(response["result"]):  # latest contributions first
            self.timestamps.append(isoparse(c["toTimestamp"]))
            self.contrib_abs.append(c["value"])
            self.contrib_sum += c["value"]
        self.result.timestamp_osm = self.timestamps[0]

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
        self.result.value = get_median_year(self.contrib_rel)

        if self.contrib_sum < self.threshold_low_contributions:
            pass
        elif self.result.value >= self.t1:
            self.result.class_ = 1
            label = "red"
        elif self.t1 > self.result.value >= self.t2:
            self.result.class_ = 2
            label = "yellow"
        elif self.t2 > self.result.value >= self.t3:
            self.result.class_ = 3
            label = "yellow"
        elif self.t3 > self.result.value >= self.t4:
            self.result.class_ = 4
            label = "green"
        elif self.t4 > self.result.value:
            self.result.class_ = 5
            label = "green"
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
            years=self.result.value,
            topic_name=self.topic.name,
            end_date=self.timestamps[0].strftime("%Y-%m-%d"),
            elements=int(self.contrib_sum),
            green=round(sum(self.contrib_rel[: self.t2]) * 100, 2),  # cumulative
            yellow=round(sum(self.contrib_rel[self.t2 : self.t1]) * 100, 2),
            red=round(sum(self.contrib_rel[self.t1 :]) * 100, 2),
            median_years=self.result.value,
            threshold_green=self.t2 - 1,
            threshold_yellow_start=self.t2,
            threshold_yellow_end=self.t1 - 1,
            threshold_red=self.t1,
            label_description=label_description,
        )

        last_edited_year = get_how_many_years_no_activity(self.contrib_abs)
        if last_edited_year > 0:
            self.result.description += (
                f" Attention: There was no mapping activity for "
                f"{last_edited_year} year(s) in this region."
            )

    def create_figure(self):
        colors = []
        for i in range(len(self.contrib_rel)):
            if i < self.t3:
                colors.append("green")
            elif i < self.t1:
                colors.append("yellow")
            elif i >= self.t1:
                colors.append("red")

        fig = pgo.Figure(
            data=pgo.Bar(
                x=self.timestamps,
                y=self.contrib_rel,
                marker_color=colors,
                xperiod0=self.timestamps[-1],
                xperiod="M12",
                xperiodalignment="start",
                hovertemplate=(
                    "%{y} of features (%{customdata})<br>"
                    "last modified until %{x}<extra></extra>"
                ),
                customdata=self.contrib_abs,
            )
        )
        if self.result.value is not None:
            start = self.timestamps[self.result.value]
            end = self.timestamps[0]
            # Workaround setting text annotation for data with date-time:
            # https://github.com/plotly/plotly.py/issues/3065
            x0 = (start - relativedelta(months=6)).timestamp() * 1000
            x1 = (end + relativedelta(months=6)).timestamp() * 1000
            fig.add_vrect(
                x0=x0,
                x1=x1,
                annotation_text=(
                    "In this time period at least 50%<br>of features have been edited."
                ),
                annotation_position="top",
                fillcolor="gray",
                layer="below",
                line_width=0,
                opacity=0.25,
            )

        y_min = min(self.contrib_rel)
        y_max = max(self.contrib_rel) * 1.05

        fig.add_trace(
            pgo.Scatter(
                x=[x0, x0, x1, x1, x0],
                y=[y_min, y_max, y_max, y_min, y_min],
                fill="toself",
                mode="lines",
                name="",
                text="In this time period at least 50%<br>of features have been edited",
                line_width=0,
                opacity=0.25,
                fillcolor="gray",
                hoverlabel=dict(bgcolor="lightgray"),
            )
        )
        fig.update_layout(
            hovermode="x",
            yaxis_range=[0, y_max],
            showlegend=False,
            title_text=("Currentness"),
        )
        fig.update_xaxes(
            title_text="Interval: {}".format(self.interval),
            ticklabelmode="period",
            dtick="M12",
            tick0=self.timestamps[-1],
        )
        fig.update_yaxes(
            title_text="Percentage of Contributions",
            tickformat=".0%",
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

        # Legacy support for SVGs
        img_bytes = fig.to_image(format="svg")
        self.result.svg = img_bytes.decode("utf-8")


def get_how_many_years_no_activity(contributions: list) -> int:
    """Get the number of years since today when the last contribution has been made."""
    for year, contrib in enumerate(contributions):  # latest contribution first
        if contrib != 0:
            return year


def get_median_year(contributions_rel: list) -> int:
    """Get the number of years since today when 50% of contributions have been made."""
    contrib_rel_cum = 0
    for year, contrib in enumerate(contributions_rel):  # latest contribution first
        contrib_rel_cum += contrib
        if contrib_rel_cum >= 0.5:
            return year
