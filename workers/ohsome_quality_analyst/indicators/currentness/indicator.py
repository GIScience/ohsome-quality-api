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
    """

    def __init__(
        self,
        layer: Layer,
        feature: geojson.Feature,
    ) -> None:
        super().__init__(layer=layer, feature=feature)
        self.threshold_class_5 = 1.0
        self.threshold_class_4 = 0.8
        self.threshold_class_3 = 0.6
        self.threshold_class_2 = 0.2
        self.element_count = None
        self.contribution_sum = 0
        self.contributions_rel = {}
        self.contributions_abs = {}
        self.ratio = {}

    async def preprocess(self) -> None:
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        # time_range for all years since 2008 and curr_year_range for the ongoing year
        start = "2008-01-01"
        self.end = latest_ohsome_stamp.strftime("%Y-%m-%d")
        time_range = "{0}/{1}/{2}".format(start, self.end, "P1Y")
        curr_year_start = "{0}-01-01".format(latest_ohsome_stamp.year)
        curr_year_range = "{0}/{1}".format(curr_year_start, self.end)

        response = await ohsome_client.query(self.layer, self.feature)
        self.element_count = response["result"][0]["value"]
        self.result.timestamp_osm = dateutil.parser.isoparse(
            response["result"][0]["timestamp"]
        )
        response_contributions = await ohsome_client.query(
            self.layer,
            self.feature,
            time=time_range,
            count_latest_contributions=True,
        )
        for year in response_contributions["result"]:
            time = dateutil.parser.isoparse(year["fromTimestamp"])
            count = year["value"]
            self.contributions_abs[time.strftime("%Y")] = count

        curr_year_response_contributions = await ohsome_client.query(
            self.layer,
            self.feature,
            time=curr_year_range,
            count_latest_contributions=True,
        )
        time = dateutil.parser.isoparse(
            curr_year_response_contributions["result"][0]["fromTimestamp"]
        )
        count = curr_year_response_contributions["result"][0]["value"]
        self.contributions_abs[time.strftime("%Y")] = count

    def calculate(self) -> None:
        """
        Calculate the years since over 50% of the elements were last edited.
        For each year 0.1 is subtracted from the result value.
        """
        logging.info(f"Calculation for indicator: {self.metadata.name}")

        self.contribution_sum = sum(self.contributions_abs.values())
        # It can be that features are counted, but have been deleted since.
        if self.element_count == 0:
            self.result.description = (
                "In the area of interest no features "
                "matching the filter are present today."
            )
            return
        contributions_share = self.contribution_sum
        last_edited_year = ""
        years_since_start = len(self.contributions_abs)
        green_contributions_rel = 0
        yellow_contributions_rel = 0
        red_contributions_rel = 0
        # determine the percentage of elements that were last edited in that year
        for year in self.contributions_abs:
            self.ratio[year] = (contributions_share / self.contribution_sum) * 100
            contributions_share -= self.contributions_abs[year]
            self.contributions_rel[year] = (
                self.contributions_abs[year] / self.contribution_sum
            ) * 100
            if self.contributions_rel[year] != 0:
                last_edited_year = year
            if years_since_start <= 3:
                green_contributions_rel += self.contributions_rel[year]
            elif years_since_start <= 7:
                yellow_contributions_rel += self.contributions_rel[year]
            else:
                red_contributions_rel += self.contributions_rel[year]
            years_since_start -= 1
        self.years_since_last_edit = int(self.result.timestamp_oqt.year) - int(
            last_edited_year
        )
        percentage_contributions = 0
        self.median_year = ""
        for year in self.contributions_rel:
            percentage_contributions += self.contributions_rel[year]
            if percentage_contributions < 50:
                continue
            else:
                self.median_year = year
                break
        median_diff = int(self.result.timestamp_oqt.year) - int(self.median_year)
        if median_diff <= 1:
            self.result.value = 1
        else:
            self.result.value = 1.0 - (median_diff / 10)
        if self.result.value < 0.0:
            self.result.value = 0.0

        if last_edited_year != str(self.result.timestamp_oqt.year):
            years_without_mapping = (
                "Attention: There was no mapping"
                " activity after {0} in this region.".format(last_edited_year)
            )
        else:
            years_without_mapping = ""
        self.result.description = Template(self.metadata.result_description).substitute(
            years=median_diff,
            layer_name=self.layer.name,
            end=self.end,
            elements=self.contribution_sum,
            green=round(green_contributions_rel, 3),
            yellow=round(yellow_contributions_rel, 3),
            red=round(red_contributions_rel, 3),
            median_years=median_diff,
        )

        if self.result.value >= self.threshold_class_5:
            self.result.class_ = 5
            self.result.description = (
                self.result.description + self.metadata.label_description["green"]
            )
        elif self.result.value >= self.threshold_class_4:
            self.result.class_ = 4
            self.result.description = (
                self.result.description + self.metadata.label_description["green"]
            )
        elif self.result.value >= self.threshold_class_3:
            self.result.class_ = 3
            self.result.description = (
                self.result.description + self.metadata.label_description["yellow"]
            )
        elif self.result.value >= self.threshold_class_2:
            self.result.class_ = 2
            self.result.description = (
                self.result.description + self.metadata.label_description["yellow"]
            )
        elif self.result.value < self.threshold_class_2:
            self.result.class_ = 1
            self.result.description = (
                self.result.description + self.metadata.label_description["red"]
            )
        else:
            raise ValueError("Ratio has an unexpected value.")
        self.result.description += years_without_mapping

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
        year_range = len(self.contributions_rel)
        patches = ax.bar(
            self.contributions_rel.keys(),
            height=self.contributions_rel.values(),
            edgecolor="black",
        )
        cnt = year_range
        for patch in patches:
            if cnt <= self.years_since_last_edit:
                ax.text(
                    patch.get_x(),
                    max(self.contributions_rel.values()) / 2,
                    "!",
                    fontdict={"fontsize": 26},
                )
            if cnt >= 8:
                patch.set_facecolor("red")
                cnt -= 1
            elif cnt >= 4:
                patch.set_facecolor("yellow")
                cnt -= 1
            else:
                patch.set_facecolor("green")
                cnt -= 1
        plt.axvline(
            x=self.median_year,
            linestyle=":",
            color="black",
            label="Median Year: {0}".format(self.median_year),
        )
        plt.xticks(list(self.contributions_rel.keys())[::2])
        plt.xlabel("Year")
        plt.ylabel("Percentage of contributions")
        plt.title("Total Contributions: %i" % self.contribution_sum)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg", bbox_inches="tight")
        self.result.svg = img_data.getvalue()
        plt.close("all")
