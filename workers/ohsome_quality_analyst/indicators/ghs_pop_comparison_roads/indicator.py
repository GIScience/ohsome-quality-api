import logging
from io import StringIO
from string import Template

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
from asyncpg import Record
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.utils.definitions import get_attribution


class GhsPopComparisonRoads(BaseIndicator):
    """Set number of features and population into perspective."""

    def __init__(
        self,
        layer_name: str,
        feature: Feature,
    ) -> None:
        super().__init__(layer_name=layer_name, feature=feature)
        # Those attributes will be set during lifecycle of the object.
        self.pop_count = None
        self.area = None
        self.pop_count_per_sqkm = None
        self.feature_length = None
        self.feature_length_per_sqkm = None

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "GHSL"])

    def green_threshold_function(self, pop_per_sqkm) -> float:
        """Return road density threshold for green label."""
        if pop_per_sqkm < 5000:
            return pop_per_sqkm / 500
        else:
            return 10

    def yellow_threshold_function(self, pop_per_sqkm) -> float:
        """Return road density threshold for yellow label."""
        if pop_per_sqkm < 5000:
            return pop_per_sqkm / 1000
        else:
            return 5

    async def preprocess(self) -> None:
        pop_count, area = await self.get_zonal_stats_population()

        if pop_count is None:
            pop_count = 0
        self.area = area
        self.pop_count = pop_count

        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=self.feature.geometry
        )
        # results in meter, we need km
        self.feature_length = query_results["result"][0]["value"] / 1000
        timestamp = query_results["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        self.feature_length_per_sqkm = self.feature_length / self.area
        self.pop_count_per_sqkm = self.pop_count / self.area

    def calculate(self) -> None:
        description = Template(self.metadata.result_description).substitute(
            pop_count=round(self.pop_count),
            area=round(self.area, 1),
            pop_count_per_sqkm=round(self.pop_count_per_sqkm, 1),
            feature_length_per_sqkm=round(self.feature_length_per_sqkm, 1),
        )

        green_road_density = self.green_threshold_function(self.pop_count_per_sqkm)
        yellow_road_density = self.yellow_threshold_function(self.pop_count_per_sqkm)

        if self.pop_count_per_sqkm == 0:
            return
        # road density is compliant to the green values or even higher
        elif self.feature_length_per_sqkm >= green_road_density:
            self.result.value = 1.0
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
            self.result.label = "green"
        # road density is too small, none, or too short roads
        elif self.feature_length_per_sqkm < yellow_road_density:
            self.result.value = 0.0
            self.result.description = (
                description + self.metadata.label_description["red"]
            )
            self.result.label = "red"
        # road density is compliant to the yellow values
        # we assume there could be more roads mapped
        else:
            self.result.value = 0.5
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
            self.result.label = "yellow"

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("Road density against \npeople per $km^2$")
        ax.set_xlabel("Population Density [$1/km^2$]")
        ax.set_ylabel("Road density [$km/km^2$]")

        # Set x max value based on area
        if self.pop_count_per_sqkm < 100:
            max_area = 10
        else:
            max_area = round(self.pop_count_per_sqkm * 2 / 10) * 10
        x = np.linspace(0, max_area, 100)
        # Plot thresholds as line.
        y1 = [self.green_threshold_function(xi) for xi in x]
        y2 = [self.yellow_threshold_function(xi) for xi in x]
        line = ax.plot(
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
        ax.fill_between(
            x,
            y1,
            max(max(y1), self.feature_length_per_sqkm),
            alpha=0.5,
            color="green",
        )

        # Plot pont as circle ("o").
        ax.plot(
            self.pop_count_per_sqkm,
            self.feature_length_per_sqkm,
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        img_data = StringIO()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()
        logging.debug("Successful SVG figure creation")
        plt.close("all")

    async def get_zonal_stats_population(self) -> Record:
        """Derive zonal population stats for given GeoJSON geometry.

        This is based on the Global Human Settlement Layer Population.
        """
        logging.info("Get population inside polygon")
        query = """
            SELECT
            SUM(
                (public.ST_SummaryStats(
                    public.ST_Clip(
                        rast,
                        st_setsrid(public.ST_GeomFromGeoJSON($1), 4326)
                    )
                )
            ).sum) population
            ,public.ST_Area(
                st_setsrid(public.ST_GeomFromGeoJSON($2)::public.geography, 4326)
            ) / (1000*1000) as area_sqkm
            FROM ghs_pop
            WHERE
             public.ST_Intersects(
                rast,
                st_setsrid(public.ST_GeomFromGeoJSON($3), 4326)
             )
            """
        data = tuple([str(self.feature.geometry)] * 3)
        async with db_client.get_connection() as conn:
            return await conn.fetchrow(query, *data)
