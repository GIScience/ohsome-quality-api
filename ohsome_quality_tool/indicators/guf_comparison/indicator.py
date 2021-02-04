import json
import os
from io import StringIO
from math import ceil
from string import Template

import matplotlib.pyplot as plt
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.ohsome import client as ohsome_client
from ohsome_quality_tool.utils.auth import PostgresDB
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger


class GufComparison(BaseIndicator):
    """Comparison of the Buildup Area in the GUF Dataset and OSM"""

    def __init__(
        self,
        dataset,
        feature_id,
        layer_name: str = "building_area",
        bpolys: FeatureCollection = "",
    ) -> None:
        super().__init__(
            dataset=dataset,
            feature_id=feature_id,
            layer_name=layer_name,
            bpolys=bpolys,
        )
        self.threshold_high: float = 0.6
        self.threshold_low: float = 0.2
        self.area: float = None
        self.guf_built_up_area: float = None
        self.osm_built_up_area: float = None
        self.ratio: float = None

    def preprocess(self) -> None:
        logger.info(f"Preprocessing for indicator: {self.metadata.name}")
        db = PostgresDB()

        directory = os.path.dirname(os.path.abspath(__file__))
        aoi_geom = json.dumps(self.bpolys["features"][0]["geometry"])
        # Get total area and built-up area (GUF) from Geodatabase in km^2 for AOI
        sql_file = os.path.join(directory, "query.sql")
        with open(sql_file) as reader:
            query = reader.read()
        result = db.retr_query(query=query, data=(aoi_geom, aoi_geom, aoi_geom))
        logger.info(result)
        self.area = result[0][0] / 1000000  # m^2 to km^2
        self.guf_built_up_area = result[0][1] / 1000000

        # Get OSM building area from ohsome API in km^2 for AOI
        query_results = ohsome_client.query(
            layer=self.layer,
            bpolys=json.dumps(self.bpolys),
        )
        self.osm_built_up_area = (
            query_results["buildings"]["result"][0]["value"] / 1000000
        )

    def calculate(self) -> None:
        logger.info(f"Calculation for indicator: {self.metadata.name}")
        self.ratio = self.guf_built_up_area / self.osm_built_up_area
        description = Template(self.metadata.result_description).substitute(
            ratio=self.ratio
        )

        if self.ratio <= self.threshold_low:
            value = TrafficLightQualityLevels.RED.value
            description += self.metadata.label_description["red"]
        elif self.ratio <= self.threshold_high:
            value = TrafficLightQualityLevels.YELLOW.value
            description += self.metadata.label_description["yellow"]
        else:
            value = TrafficLightQualityLevels.GREEN.value
            description += self.metadata.label_description["green"]

        label = TrafficLightQualityLevels(ceil(self.result.value))

        self.result.label = label
        self.result.value = value
        self.result.description = description

    def create_figure(self) -> None:
        """Create a plot and return as SVG string."""
        logger.info(f"Create figure for indicator: {self.metadata.name}")
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Built-Up Area")
        ax.set_xlabel("Global Urban Footprint [%]")
        ax.set_ylabel("OpenStreetMap [%]")
        ax.set_xlim((0, 100))
        ax.set_ylim((0, 100))

        # Plot thresholds as line.
        x = [0, 100]
        y1 = [0, 100 * self.threshold_high]
        y2 = [0, 100 * self.threshold_low]
        line = line = ax.plot(
            x,
            y1,
            color="black",
            label="Threshold A",
        )
        plt.setp(line, linestyle="--")

        line = ax.plot(
            x,
            y2,
            color="black",
            label="Threshold B",
        )
        plt.setp(line, linestyle=":")

        # Fill in space between thresholds
        ax.fill_between(x, y2, 0, alpha=0.5, color="red")
        ax.fill_between(x, y1, y2, alpha=0.5, color="yellow")
        ax.fill_between(x, y1, 100, alpha=0.5, color="green")

        # Plot point as circle ("o").
        ax.plot(
            self.guf_built_up_area * 100 / self.area,
            self.osm_built_up_area * 100 / self.area,
            "o",
            color="black",
            label=(
                f"Indicator value: {round(self.ratio)}"
                # f"{round(self.guf_built_up_area)}/"
                # f"{round(self.osm_built_up_area)} "
                # f"[$km^2$]"
            ),
        )

        ax.legend()

        img_data = StringIO.StringIO()
        plt.savefig(img_data, format="svg")
        img_data.seek(0)  # rewind the data
        self.result.svg = img_data.buf  # this is svg data
        logger.info(f"Got svg-figure string for indicator {self.metadata.name}")
        plt.close("all")
