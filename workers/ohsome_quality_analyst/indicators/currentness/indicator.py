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
        super().__init__(
            layer=layer,
            feature=feature,
        )
        self.threshold_yellow = 0.6
        self.threshold_red = 0.2
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

        response = await ohsome_client.query(self.layer, self.feature.geometry)
        self.element_count = response["result"][0]["value"]
        self.result.timestamp_osm = dateutil.parser.isoparse(
            response["result"][0]["timestamp"]
        )
        response_contributions = await ohsome_client.query(
            self.layer,
            self.feature.geometry,
            time=time_range,
            endpoint="contributions/latest/count",
        )
        for year in response_contributions["result"]:
            time = dateutil.parser.isoparse(year["fromTimestamp"])
            count = year["value"]
            self.contributions_abs[time.strftime("%Y")] = count

        curr_year_response_contributions = await ohsome_client.query(
            self.layer,
            self.feature.geometry,
            time=curr_year_range,
            endpoint="contributions/latest/count",
        )
        time = dateutil.parser.isoparse(
            curr_year_response_contributions["result"][0]["fromTimestamp"]
        )
        count = curr_year_response_contributions["result"][0]["value"]
        self.contributions_abs[time.strftime("%Y")] = count

    def calculate(self) -> None:
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
        # determine the percentage of elements that were last edited in that year
        for year in self.contributions_abs:
            self.ratio[year] = (contributions_share / self.contribution_sum) * 100
            contributions_share -= self.contributions_abs[year]
            self.contributions_rel[year] = (
                self.contributions_abs[year] / self.contribution_sum
            ) * 100
            if self.contributions_rel[year] != 0:
                last_edited_year = year
        years_since_last_edit = int(self.result.timestamp_oqt.year) - int(
            last_edited_year
        )
        percentage_contributions = 0
        median_year = ""
        for year in self.contributions_rel:
            percentage_contributions += self.contributions_rel[year]
            if percentage_contributions < 50:
                continue
            else:
                median_year = year
                break
        median_diff = int(self.result.timestamp_oqt.year) - int(median_year)
        if median_diff <= 1:
            param_1 = 1
        elif median_diff <= 4:
            param_1 = 0.6
        else:
            param_1 = 0.2
        if years_since_last_edit <= 1:
            param_2 = 1
        elif years_since_last_edit <= 4:
            param_2 = 0.6
        else:
            param_2 = 0.2
        self.result.value = (param_1 + param_2) / 2
        if median_diff == 0:
            median_diff = "this year"
        elif median_diff == 1:
            median_diff = "in the last year"
        else:
            median_diff = "in the last {0} years".format(median_diff)
        self.result.description = Template(self.metadata.result_description).substitute(
            years=median_diff,
            layer_name=self.layer.name,
            end=self.end,
            elements=self.contribution_sum,
        )

        if self.result.value >= self.threshold_yellow:
            self.result.label = "green"
            self.result.description = (
                self.result.description + self.metadata.label_description["green"]
            )
        elif self.result.value >= self.threshold_red:
            self.result.label = "yellow"
            self.result.description = (
                self.result.description + self.metadata.label_description["yellow"]
            )
        elif self.result.value < self.threshold_red:
            self.result.label = "red"
            self.result.description = (
                self.result.description + self.metadata.label_description["red"]
            )
        else:
            raise ValueError("Ratio has an unexpected value.")

    def create_figure(self) -> None:
        """Create a plot.

        Shows the percentage of contributions for each year.
        """
        if self.element_count == 0:
            return
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        x = list(self.ratio.keys())
        ax.plot(
            x,
            self.ratio.values(),
            color="b",
            label="Percentage of contributions (cumulative)",
        )
        ax.bar(
            list(self.contributions_rel.keys()),
            self.contributions_rel.values(),
            color=self.result.label,
            label="Percentage of contributions (year) ",
        )
        ax.set_xticks(x[::2])
        plt.ylabel("Percentage of contributions")
        plt.title("Total Contributions: %i" % self.contribution_sum)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.45))
        fig.subplots_adjust(bottom=0.3)
        fig.tight_layout()
        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
