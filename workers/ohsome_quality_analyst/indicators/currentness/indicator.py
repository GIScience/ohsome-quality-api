import logging
from io import StringIO
from string import Template

import dateutil.parser
import geojson
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client


class Currentness(BaseIndicator):
    """Percentage of features that have been edited over the given time range."""

    def __init__(
        self,
        layer_name: str,
        feature: geojson.Feature,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            feature=feature,
        )
        self.threshold_yellow = 0.6
        self.threshold_red = 0.2
        self.element_count = None
        self.contribution_sum = 0
        self.contributions = {}
        self.ratio = {}

    async def preprocess(self) -> None:
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        start = (latest_ohsome_stamp - relativedelta(years=13)).strftime("%Y-%m-%d")
        end = latest_ohsome_stamp.strftime("%Y-%m-%d")
        self.time_range = "{0}/{1}/{2}".format(start, end, "P1Y")

        response = await ohsome_client.query(
            layer=self.layer,
            bpolys=self.feature.geometry,
        )
        self.element_count = response["result"][0]["value"]
        self.result.timestamp_osm = dateutil.parser.isoparse(
            response["result"][0]["timestamp"]
        )
        url = "https://api.ohsome.org/v1/contributions/latest/count"
        data = {
            "bpolys": geojson.dumps(
                geojson.FeatureCollection(
                    [geojson.Feature(geometry=self.feature.geometry)]
                )
            ),
            "time": self.time_range,
            "filter": self.layer.filter,
        }
        response_contributions = await ohsome_client.query_ohsome_api(url, data)
        for year in response_contributions["result"]:
            time = dateutil.parser.isoparse(year["fromTimestamp"])
            count = year["value"]
            self.contributions[time.strftime("%Y")] = count

    def calculate(self) -> None:
        logging.info(f"Calculation for indicator: {self.metadata.name}")

        self.contribution_sum = sum(self.contributions.values())
        # It can be that features are counted, but have been deleted since.
        if self.element_count == 0:
            self.result.description = (
                "In the area of intrest no features matching the filter are present."
            )
            return
        contributions_rel = self.contribution_sum
        contributions_list = []
        last_edited_year = ""
        for year in self.contributions:
            self.ratio[year] = (contributions_rel / self.contribution_sum) * 100
            contributions_rel -= self.contributions[year]
            self.contributions[year] = (
                self.contributions[year] / self.contribution_sum
            ) * 100
            contributions_list.append(self.contributions[year])
            if self.contributions[year] != 0:
                last_edited_year = year
        years_since_last_edit = (
            int(self.result.timestamp_oqt.year) - 1 - int(last_edited_year)
        )
        percentage_contributions = 0
        median_year = ""
        for year in self.contributions:
            percentage_contributions += self.contributions[year]
            if percentage_contributions < 50:
                continue
            else:
                median_year = year
                break
        median_diff = int(self.result.timestamp_oqt.year) - 1 - int(median_year)
        param_1 = 0
        if median_diff <= 1:
            param_1 = 1
        elif median_diff <= 4:
            param_1 = 0.6
        else:
            param_1 = 0.2
        param_2 = 0
        if years_since_last_edit <= 1:
            param_2 = 1
        elif years_since_last_edit <= 4:
            param_2 = 0.6
        else:
            param_2 = 0.2
        self.result.value = (param_1 + param_2) / 2

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
        plt.title("Total Contributions: %i" % self.contribution_sum)
        plt.legend()
        fig.tight_layout()
        plt.show()
        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()  # this is svg data
        logging.debug("Successful SVG figure creation")
        plt.close("all")
