import logging
import os
from functools import cache

import geojson
import plotly.graph_objects as pgo
import psycopg
import yaml
from async_lru import alru_cache
from dateutil import parser
from geojson import Feature
from numpy import mean

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.definitions import Color, get_attribution
from ohsome_quality_api.geodatabase import client as db_client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic


class RoadComparison(BaseIndicator):
    def __init__(
        self,
        topic: BaseTopic,
        feature: Feature,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )
        # The result is the ratio of area within coverage (between 0-1) or an empty list
        #
        # TODO: Evaluate thresholds
        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow

        self.data_ref: dict[str, dict] = {}
        self.area_cov: dict[str, float | None] = {}
        self.ratio: dict[str, float | None] = {}
        self.length_matched: dict[str, float | None] = {}
        self.length_total: dict[str, float | None] = {}
        self.length_osm: dict[str, float | None] = {}
        self.warnings: dict[str, str | None] = {}
        # self.data_ref: list = load_reference_datasets()  # reference datasets
        for key, val in load_datasets_metadata().items():
            self.data_ref[key] = val
            self.area_cov[key] = None  # covered area [%]
            self.length_matched[key] = None
            self.length_total[key] = None
            self.warnings[key] = None
            self.length_osm[key] = None
            self.ratio[key] = None

    @classmethod
    async def coverage(cls, inverse=False) -> list[Feature]:
        # TODO: could also return a Feature Collection
        features = []
        datasets = load_datasets_metadata()
        for val in datasets.values():
            if inverse:
                table = val["coverage"]["inversed"]
            else:
                table = val["coverage"]["simple"]
            feature = await db_client.get_reference_coverage(table)
            feature.properties.update({"refernce_dataset": val["name"]})
            features.append(feature)
        return features

    @classmethod
    def attribution(cls) -> str:
        # TODO: add attribution
        return get_attribution(["OSM"])

    async def preprocess(self) -> None:
        for key, val in self.data_ref.items():
            # get coverage [%]
            self.area_cov[key] = await db_client.get_intersection_area(
                self.feature,
                val["coverage"]["simple"],
            )
            self.warnings[key] = self.check_major_edge_cases(key)
            if self.warnings[key] != "":
                continue

            # clip input geom with coverage of reference dataset
            feature = await db_client.get_intersection_geom(
                self.feature,
                val["coverage"]["simple"],
            )

            # get matched ratio
            (
                self.length_matched[key],
                self.length_total[key],
            ) = await get_matched_roadlengths(geojson.dumps(feature), val["table_name"])
            if self.length_total[key] is None:
                self.length_total[key] = 0
                self.length_matched[key] = 0
            elif self.length_matched[key] is None:
                self.length_matched[key] = 0

            # get osm road length
            result = await ohsome_client.query(self.topic, feature)
            value = result["result"][0]["value"] or 0.0  # if None
            self.length_osm[key] = value
            timestamp = result["result"][0]["timestamp"]
            self.result.timestamp_osm = parser.isoparse(timestamp)

    def calculate(self) -> None:
        # TODO: put checks into check_corner_cases. Let result be undefined.
        edge_cases = [self.check_major_edge_cases(k) for k in self.data_ref.keys()]
        if all(edge_cases):
            self.result.description += (
                " None of the reference datasets covers the area-of-interest."
            )
            return
        self.result.description = ""
        for key in self.data_ref.keys():
            # if None in (self.ratio[key], self.area_cov[key], self.data_ref[key]):
            if self.warnings[key] != "":
                self.result.description += self.warnings[key] + "\n"
                continue

            self.warnings[key] += self.check_minor_edge_cases(key)
            try:
                self.ratio[key] = self.length_matched[key] / self.length_total[key]
            except ZeroDivisionError:
                self.ratio[key] = None
                self.warnings[key] += (
                    f"Warning: Reference dataset {self.data_ref[key]['name']} covers "
                    f"AoI with {round(self.area_cov[key] * 100, 2)}%, but has no "
                    "road length. No quality estimation with reference is possible. "
                )

            self.result.description += self.warnings[key] + "\n"

        ratios = [v for v in self.ratio.values() if v is not None]
        if ratios:
            self.result.value = float(mean(ratios))
        else:
            self.result.description += (
                "Warning: None of the reference datasets has "
                "roads mapped in this area. "
            )

        if self.result.value is not None:
            if self.result.value >= self.th_high:
                self.result.class_ = 5
            elif self.th_high > self.result.value >= self.th_low:
                self.result.class_ = 3
            elif self.th_low > self.result.value >= 0:
                self.result.class_ = 1

        label_description = self.metadata.label_description[self.result.label]
        self.result.description += label_description

    def create_figure(self) -> None:
        edge_cases = [self.check_major_edge_cases(k) for k in self.data_ref.keys()]
        if self.result.label == "undefined" and all(edge_cases):
            logging.info(
                "Result is undefined and major edge case is present."
                " Skipping figure creation."
            )
            return

        fig = pgo.Figure()

        # Plot inner Pie (Traffic Light)
        fig.add_trace(
            pgo.Pie(
                values=[self.th_low, self.th_high - self.th_low, 1 - self.th_high],
                labels=["Bad", "Medium", "Good"],
                marker_colors=["red", "yellow", "green"],
                sort=False,
                textinfo="none",
            )
        )

        ref_name = []
        ref_ratio = []
        ref_color = []
        for key, val in self.ratio.items():
            if val is None:
                continue
            ref_name.append(self.data_ref[key]["name"])
            ref_color.append(Color[self.data_ref[key]["color"]].value)
            ref_ratio.append(val)
        ratio = 1 / (len(ref_name) + 1)
        hole_list = [ratio * (i + 1) for i in range(len(ref_name))]
        for i, (name, ratio) in enumerate(zip(ref_name, ref_ratio)):
            if isinstance(ratio, type(str)):
                values = [1]
                labels = [""]
                marker_colors = ["#FFFFFF"]
            else:
                values = [ratio, 1 - ratio]
                labels = [
                    f"{name} <br> Ratio: {round(ratio, 2)}",
                    " ",
                ]
                marker_colors = [ref_color[i], "#FFFFFF"]

            fig.add_trace(
                pgo.Pie(
                    values=values,
                    labels=labels,
                    sort=False,
                    hole=hole_list[i],
                    marker_colors=marker_colors,
                    textinfo="none",
                )
            )
        fig.update_layout(
            title={
                "text": "Ratio between all features and filtered ones",
                "y": 0.95,
                "x": 0.5,
                "yanchor": "top",
            },
            legend={
                "y": 0.5,
                "x": 0.75,
            },
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def check_major_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.area_cov[dataset]
        if coverage is None or coverage == 0.00:
            return f"Reference dataset {dataset} does not cover area-of-interest. "
        elif coverage < 0.10:
            return (
                "Only {:.2f}% of the area-of-interest is covered ".format(
                    coverage * 100
                )
                + f"by the reference dataset ({dataset}). "
                + f"No quality estimation with reference {dataset} is possible."
            )
        else:
            return ""

    def check_minor_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.area_cov[dataset]
        if coverage < 0.95:
            return (
                f"Warning: Reference data {dataset} does "
                f"not cover the whole input geometry. "
                + "Input geometry is clipped to the coverage."
                " Result is only calculated"
                " for the intersection area. "
            )
        else:
            return ""

    def format_sources(self):
        sources = []
        for dataset in self.data_ref.values():
            if dataset["link"] is not None:
                sources.append(f"<a href='{dataset['link']}'>" f"{dataset['name']}</a>")
            else:
                sources.append(f"{dataset}")
        result = ", ".join(sources)
        return result


# alru needs hashable type, therefore, use string instead of Feature
@alru_cache
async def get_matched_roadlengths(
    feature_str: str, table_name: str
) -> tuple[float, float]:
    """Get the building area for a AoI from the EUBUCCO dataset."""
    # TODO: https://github.com/GIScience/ohsome-quality-api/issues/746
    file_path = os.path.join(db_client.WORKING_DIR, "get_matched_roads.sql")
    with open(file_path, "r") as file:
        query = file.read()
    dns = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("postgres_host"),
        port=get_config_value("postgres_port"),
        database=get_config_value("postgres_db"),
        user=get_config_value("postgres_user"),
        password=get_config_value("postgres_password"),
    )
    feature = geojson.loads(feature_str)
    table_name = table_name.replace(" ", "_")
    geom = geojson.dumps(feature.geometry)
    async with await psycopg.AsyncConnection.connect(dns) as con:
        async with con.cursor() as cur:
            await cur.execute(query.format(table_name=table_name), (geom,))
            res = await cur.fetchone()
    return res[0], res[1]


@cache
def load_datasets_metadata() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
