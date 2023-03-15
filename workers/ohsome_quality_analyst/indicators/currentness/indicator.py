import logging
from io import StringIO
from string import Template

import dateutil.parser
import geojson
import matplotlib.pyplot as plt

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.ohsome import client as ohsome_client


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
        layer: Layer,
        feature: geojson.Feature,
    ) -> None:
        super().__init__(layer=layer, feature=feature)
        self.threshold_4 = 2
        self.threshold_3 = 3
        self.threshold_2 = 4
        self.threshold_1 = 8
        self.element_count = None
        self.contributions_sum = None
        self.contributions_rel = {}  # yearly interval
        self.contributions_abs = {}  # yearly interval
        self.start = "2008-01-01"
        self.end = None
        self.low_contributions_threshold = 0

    async def preprocess(self) -> None:
        """Get absolute number of contributions for each year since given start date"""
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        self.end = latest_ohsome_stamp.strftime("%Y-%m-%d")
        past_years_interval = "{0}/{1}/{2}".format(self.start, self.end, "P1Y")
        current_year_interval = "{0}/{1}".format(
            "{0}-01-01".format(latest_ohsome_stamp.year),
            self.end,
        )
        # Fetch number of features
        response = await ohsome_client.query(self.layer, self.feature)
        self.element_count = response["result"][0]["value"]
        self.result.timestamp_osm = dateutil.parser.isoparse(
            response["result"][0]["timestamp"]
        )
        # Fetch all contributions of past years
        contributions_yearly = await ohsome_client.query(
            self.layer,
            self.feature,
            time=past_years_interval,
            count_latest_contributions=True,
            #  exclude deletions from the response
            contribution_type="geometryChange,creation,tagChange",
        )
        # Fetch contributions of current year
        contributions_current_year = await ohsome_client.query(
            self.layer,
            self.feature,
            time=current_year_interval,
            count_latest_contributions=True,
            contribution_type="geometryChange,creation,tagChange",
        )
        # Merge contributions
        contributions = (
            contributions_yearly["result"] + contributions_current_year["result"]
        )
        for contrib in contributions:
            time = dateutil.parser.isoparse(contrib["fromTimestamp"])
            count = contrib["value"]
            self.contributions_abs[time.strftime("%Y")] = count

    def calculate(self) -> None:
        """Calculate the years since over 50% of the elements were last edited"""
        logging.info(f"Calculation for indicator: {self.metadata.name}")

        # It can be that features have been edited, but have been deleted since.
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
            reversed(self.contributions_abs.items()),
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
        # calculate the year in which 50% of the total edits have been made
        self.median_year = get_median_year(self.contributions_rel)
        # years since last edit has been made
        self.result.value = int(self.result.timestamp_oqt.year) - self.median_year

        self.result.description = Template(self.metadata.result_description).substitute(
            years=self.result.value,
            layer_name=self.layer.name,
            end=self.end,
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
        """Create a plot.

        Shows the percentage of contributions for each year.
        """
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize, tight_layout=True)
        ax = fig.add_subplot()
        patches = ax.bar(
            self.contributions_rel.keys(),
            height=[v * 100 for v in self.contributions_rel.values()],
            edgecolor="black",
        )
        year_range = len(self.contributions_rel)
        last_edited_year = get_last_edited_year(self.contributions_abs)
        years_since_last_edit = int(self.result.timestamp_oqt.year) - last_edited_year
        for patch in patches:
            if year_range <= years_since_last_edit:
                ax.text(
                    patch.get_x(),
                    max(self.contributions_rel.values()) * 100 / 2,
                    "!",
                    fontdict={"fontsize": 26},
                )
            if year_range > self.threshold_1:
                patch.set_facecolor("red")
                year_range -= 1
            elif year_range >= self.threshold_2:
                patch.set_facecolor("yellow")
                year_range -= 1
            else:
                patch.set_facecolor("green")
                year_range -= 1
        plt.axvline(
            x=str(self.median_year),
            linestyle=":",
            color="black",
            label="Median Year: {0}".format(self.median_year),
        )
        plt.xticks(list(self.contributions_rel.keys())[::2])
        plt.xlabel("Year")
        plt.ylabel("Percentage of contributions")
        plt.title("Total Contributions: %i" % self.contributions_sum)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg", bbox_inches="tight")
        self.result.svg = img_data.getvalue()
        plt.close("all")


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
