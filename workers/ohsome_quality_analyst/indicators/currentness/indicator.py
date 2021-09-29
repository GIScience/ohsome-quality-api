import logging
from io import StringIO
from string import Template

import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client


class Currentness(BaseIndicator):
    """Percentage of features that have been edited over the past year.

    Calculated by the ratio of latest contribution count to element count.
    """

    def __init__(
        self,
        layer_name: str,
        feature: Feature,
        # datetime format: start_date/end_date/P1Y
        time_range: str = None,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            feature=feature,
        )
        # Threshold values are in percentage
        self.threshold_yellow = 0.6
        self.threshold_red = 0.2
        self.time_range = time_range
        self.element_count = None
        self.contribution_count = 0
        self.contributions = None
        self.ratio = {}

    async def preprocess(self) -> None:
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        if self.time_range is None:
            start = (latest_ohsome_stamp - relativedelta(years=10)).strftime("%Y-%m-%d")
            end = latest_ohsome_stamp.strftime("%Y-%m-%d")
            self.time_range = "{0}/{1}/{2}".format(start, end, "P1Y")

        response = await ohsome_client.query(
            layer=self.layer,
            bpolys=self.feature.geometry,
        )
        self.element_count = response["result"][0]["value"]
        self.contributions = await ohsome_client.get_contributions(
            self.feature.geometry, self.time_range, self.layer.filter
        )
        self.result.timestamp_osm = latest_ohsome_stamp

    def calculate(self) -> None:
        logging.info(f"Calculation for indicator: {self.metadata.name}")

        for year in self.contributions:
            self.contribution_count += self.contributions[year]
        # It can be that features are counted, but have been deleted since.
        if self.element_count == 0:
            self.result.description = (
                "In the area of intrest no features matching the filter are present."
            )
            return
        years_without_contributions = []
        contributions_rel = self.contribution_count
        first = True
        for year in self.contributions:
            if self.contributions[year] == 0:
                years_without_contributions.append(int(year))
            if first is True:
                first = False
                contributions_rel -= self.contributions[year]
                self.ratio[year] = 100
                self.contributions[year] = (
                    self.contributions[year] / self.contribution_count
                ) * 100
            else:
                self.ratio[year] = (contributions_rel / self.contribution_count) * 100
                contributions_rel -= self.contributions[year]
                self.contributions[year] = (
                    self.contributions[year] / self.contribution_count
                ) * 100
        arr = []
        last_edit = False
        for year in self.contributions:
            if last_edit is False:
                if int(year) in years_without_contributions:
                    continue
                else:
                    last_edit = True
                    arr.append(self.contributions[year])
            else:
                arr.append(self.contributions[year])
        median = np.median(arr)
        for year in arr:
            if year == 0.0:
                arr.remove(0.0)
        if median > 10:
            label_1 = 1.0
        else:
            label_1 = median / 10
        if len(arr) >= 9:
            label_2 = 1.0
        elif len(arr) >= 6:
            label_2 = 0.5
        else:
            label_2 = 0.0
        self.result.value = (label_1 + label_2) / 2

        description = Template(self.metadata.result_description).substitute(
            ratio=self.ratio, layer_name=self.layer.name
        )

        if self.result.value >= self.threshold_yellow:
            self.result.label = "green"
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        elif self.result.value >= self.threshold_red:
            self.result.label = "yellow"
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
        elif self.result.value < self.threshold_red:
            self.result.label = "red"
            self.result.description = (
                description + self.metadata.label_description["red"]
            )
        else:
            raise ValueError("Ratio has an unexpected value.")

    def create_figure(self) -> None:
        """Create a nested pie chart.

        Slices are ordered and plotted counter-clockwise.
        """
        if self.element_count == 0:
            return
        fig, ax = plt.subplots()
        x = list(self.ratio.keys())
        ax.plot(
            x,
            self.ratio.values(),
            color="b",
            label="Percentage of contributions (cumulative)",
        )
        ax.bar(
            list(self.contributions.keys()),
            self.contributions.values(),
            color=self.result.label,
            label="Percentage of contributions (year) ",
        )
        plt.xlabel("Year")
        plt.ylabel("Percentage of contributions")
        plt.title("Total Contributions: %i" % self.contribution_count)
        plt.legend()
        fig.tight_layout()
        plt.show()
        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
