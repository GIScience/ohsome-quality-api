import logging
from string import Template

import dateutil.parser
import geojson
import plotly.graph_objects as pgo

from ohsome_quality_analyst.indicators.base import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.topics.models import BaseTopic as Topic


class Currentness(BaseIndicator):
    """
    Ratio of all contributions that have been edited since 2008 until the
    current day in relation with years without mapping activities in the same
    time range

    Attributes:
        threshold_4 (int): Number of years it should have been since 50%
            of the items were last edited to be in the second best class
        threshold_3 (int): Number of years it should have been since 50%
            of the items were last edited to be in the second best class
        threshold_2 (int): Number of years it should have been since 50%
            of the items were last edited to be in the third best class
        threshold_1 (int): Number of years it should have been since 50%
            of the items were last edited to be in the second worst class. If
            the result is lower than this threshold, it is assigned to the worst class
    """

    def __init__(
        self,
        topic: Topic,
        feature: geojson.Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_4 = 2
        self.threshold_3 = 3
        self.threshold_2 = 4
        self.threshold_1 = 8
        self.element_count = 0
        self.contributions_sum = None
        self.contributions_rel = {}  # yearly interval
        self.contributions_abs = {}  # yearly interval
        self.start = ""
        self.end = None
        self.low_contributions_threshold = 0

    async def preprocess(self) -> None:
        """Get absolute number of contributions for each year since given start date"""
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        self.end = latest_ohsome_stamp.strftime("%Y-%m-%d")
        self.start = "2008-" + latest_ohsome_stamp.strftime("%m-%d")
        past_years_interval = "{0}/{1}/{2}".format(self.start, self.end, "P1Y")

        # Fetch all contributions of past years
        contributions = await ohsome_client.query(
            self.topic,
            self.feature,
            time=past_years_interval,
            count_latest_contributions=True,
            # exclude deletions from the response
            contribution_type="geometryChange,creation,tagChange",
        )
        years_since_today = 0
        # Merge contributions
        for contrib in reversed(contributions["result"]):
            if years_since_today == 0:
                self.result.timestamp_osm = dateutil.parser.isoparse(
                    contrib["toTimestamp"]
                )
            count = contrib["value"]
            self.contributions_abs[years_since_today] = count
            years_since_today += 1
            self.element_count += count

    def calculate(self) -> None:
        """Calculate the years since over 50% of the elements were last edited"""
        logging.info(f"Calculation for indicator: {self.metadata.name}")

        if self.element_count == 0:
            self.result.description = (
                "In the area of interest no features "
                "matching the filter are present today."
            )
            return

        # calculate relative number of contributions for each year
        self.contributions_sum = sum(self.contributions_abs.values())
        contributions_rel = {}
        contrib_rel_cum_green = 0
        contrib_rel_cum_yellow = 0
        contrib_rel_cum_red = 0
        for num_of_years, (year, contrib_abs) in enumerate(
            self.contributions_abs.items(),
            start=1,
        ):
            contrib_rel = contrib_abs / self.contributions_sum
            contributions_rel[year] = contrib_rel
            if num_of_years < self.threshold_2:
                contrib_rel_cum_green += contrib_rel
            elif num_of_years < self.threshold_1:
                contrib_rel_cum_yellow += contrib_rel
            else:
                contrib_rel_cum_red += contrib_rel
        self.contributions_rel = dict(sorted(contributions_rel.items()))
        # calculate the years since which 50% of the total edits have been made
        self.result.value = get_median_year(self.contributions_rel)

        self.result.description = Template(self.metadata.result_description).substitute(
            years=self.result.value,
            topic_name=self.topic.name,
            end_date=self.end,
            elements=int(self.contributions_sum),
            green=round(contrib_rel_cum_green * 100, 2),
            yellow=round(contrib_rel_cum_yellow * 100, 2),
            red=round(contrib_rel_cum_red * 100, 2),
            median_years=self.result.value,
            threshold_green=self.threshold_2 - 1,
            threshold_yellow_start=self.threshold_2,
            threshold_yellow_end=self.threshold_1 - 1,
            threshold_red=self.threshold_1,
        )
        if self.result.value >= self.threshold_1:
            self.result.class_ = 1
            self.result.description = (
                self.result.description + self.metadata.label_description["red"]
            )
        elif self.threshold_1 > self.result.value >= self.threshold_2:
            self.result.class_ = 2
            self.result.description = (
                self.result.description + self.metadata.label_description["yellow"]
            )
        elif self.threshold_2 > self.result.value >= self.threshold_3:
            self.result.class_ = 3
            self.result.description = (
                self.result.description + self.metadata.label_description["yellow"]
            )
        elif self.threshold_3 > self.result.value >= self.threshold_4:
            self.result.class_ = 4
            self.result.description = (
                self.result.description + self.metadata.label_description["green"]
            )
        elif self.threshold_4 > self.result.value:
            self.result.class_ = 5
            self.result.description = (
                self.result.description + self.metadata.label_description["green"]
            )
        else:
            raise ValueError("Ratio has an unexpected value.")
        last_edited_year = get_last_edited_year(self.contributions_abs)
        self.years_since_last_edit = (
            int(self.result.timestamp_oqt.year) - last_edited_year
        )
        if last_edited_year != self.result.timestamp_oqt.year:
            self.result.description += (
                "Attention: There was no mapping activity after "
                + "{0} in this region.".format(last_edited_year)
            )
        if self.contributions_sum < self.low_contributions_threshold:
            self.result.description += (
                "Attention: In this region there are very few contributions "
                + "({0}) with the given tags ".format(self.contributions_sum)
            )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        colors = []
        for i in range(len(self.contributions_rel)):
            if i < self.threshold_3:
                colors.append("green")
            elif i < self.threshold_1:
                colors.append("yellow")
            elif i >= self.threshold_1:
                colors.append("red")
        fig = pgo.Figure(
            data=pgo.Bar(
                x=list(self.contributions_rel.keys()),
                y=list(self.contributions_rel.values()),
                marker_color=colors,
                name="test",
            )
        )
        fig.add_vline(
            x=self.result.value,
            line_width=3,
            line_dash="dash",
            line_color="black",
        )
        fig.update_layout(
            title_text="Total Contributions (up to {0}): {1}".format(
                self.end, int(self.element_count)
            )
            + "<br>"
            + "The dashed line indicates the time since which more than 50% "
            "of the objects have been edited.",
        )
        fig.update_xaxes(title_text="Years since", autorange="reversed")
        fig.update_yaxes(title_text="Percentage of contributions")
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

        # Legacy support for SVGs
        img_bytes = fig.to_image(format="svg")
        self.result.svg = img_bytes.decode("utf-8")


def get_last_edited_year(contributions: dict) -> int:
    """Get the year in which the last edit has been made"""
    for year, contrib in dict(reversed(sorted(contributions.items()))).items():
        if contrib != 0:
            return int(year)


def get_median_year(contributions: dict) -> int:
    """Get the year in which 50% of the total edits have been made since first edit"""
    contrib_rel_cum = 0
    for year, contrib in dict(sorted(contributions.items())).items():
        contrib_rel_cum += contrib
        if contrib_rel_cum >= 0.5:
            return int(year)
