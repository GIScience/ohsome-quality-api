import logging
import os
from functools import cache

import geojson
import plotly.graph_objects as pgo
import psycopg
import yaml
from async_lru import alru_cache
from geojson import Feature
from numpy import mean

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.definitions import Color, get_attribution
from ohsome_quality_api.geodatabase import client as db_client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic


class RoadComparison(BaseIndicator):
    """Comparison of OSM Roads with reference data.

    Result is a ratio of the length of reference roads wich are covered by OSM roads
    to the total length of reference roads.
    """

    def __init__(
        self,
        topic: BaseTopic,
        feature: Feature,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )
        # TODO: Evaluate thresholds
        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow

        self.data_ref: dict[str, dict] = {}
        self.area_cov: dict[str, float | None] = {}
        self.length_matched: dict[str, float | None] = {}
        self.length_total: dict[str, float | None] = {}
        self.length_osm: dict[str, float | None] = {}
        self.ratio: dict[str, float | None] = {}
        self.warnings: dict[str, str | None] = {}
        # self.data_ref: list = load_reference_datasets()  # reference datasets
        for key, val in load_datasets_metadata().items():
            self.data_ref[key] = val
            self.area_cov[key] = None  # covered area [%]
            self.length_matched[key] = None
            self.length_total[key] = None
            self.length_osm[key] = None
            self.ratio[key] = None
            self.warnings[key] = None

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
            # get area covered by reference dataset [%]
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
            ) = await get_matched_roadlengths(
                geojson.dumps(feature),
                val["table_name"],
            )
            if self.length_total[key] is None:
                self.length_total[key] = 0
                self.length_matched[key] = 0
            elif self.length_matched[key] is None:
                self.length_matched[key] = 0

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
            self.result.description += (
                f"{self.data_ref[key]['name']} has a road length of "
                f"{(self.length_total[key]/1000):.2f} km, of which "
                f"{(self.length_matched[key]/1000):.2f} km are covered by roads in "
                f"OSM. "
            )

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

        ref_name = []
        ref_ratio = []
        ref_color = []
        ref_processingdate = []
        for key, val in self.ratio.items():
            if val is None:
                continue
            ref_name.append(self.data_ref[key]["name"])
            ref_color.append(Color[self.data_ref[key]["color"]].value)
            ref_processingdate.append(self.data_ref[key]["processing_date"])
            ref_ratio.append(val)

        for i, (name, ratio, date) in enumerate(
            zip(ref_name, ref_ratio, ref_processingdate)
        ):
            fig.add_trace(
                pgo.Bar(
                    x=[name],
                    y=[ratio],
                    name=f"{name} matched with OSM",
                    marker=dict(color="black", line=dict(color="black", width=1)),
                    width=0.4,
                    hovertext=f"OSM Covered: {(self.length_matched[name]/1000):.2f} km"
                    f" ({date:%b %d, %Y})",
                    hoverinfo="text",
                )
            )
            length_difference_km = (
                self.length_total[name] - self.length_matched[name]
            ) / 1000
            fig.add_trace(
                pgo.Bar(
                    x=[name],
                    y=[1 - ratio],
                    name=f"{name} not matched with OSM",
                    marker=dict(
                        color="rgba(0,0,0,0)", line=dict(color="black", width=1)
                    ),
                    width=0.4,
                    hovertext=f"Not OSM Covered: {length_difference_km:.2f} km "
                    f"({date:%b %d, %Y})",
                    hoverinfo="text",
                    text=[f"{round((ratio * 100), 2)} % of Roads covered by OSM"],
                    textposition="outside",
                )
            )

            # Update layout
            fig.update_layout(
                barmode="stack",
                title="Road Comparison",
                xaxis=dict(title="Reference Dataset"),
                yaxis=dict(title="Ratio of matched road length"),
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
    feature_str: str,
    table_name: str,
) -> tuple[float, float]:
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
            await cur.execute(
                query.format(table_name=table_name),
                (geom,),
            )
            res = await cur.fetchone()
    return res[0], res[1]


@cache
def load_datasets_metadata() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
