import logging
import os

import geojson
import plotly.graph_objects as pgo
import psycopg
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

    @classmethod
    async def coverage(cls, inverse=False) -> list[Feature]:
        # TODO: could also return a Feature Collection
        features = []
        datasets = await load_datasets_metadata()
        for val in datasets.values():
            if inverse:
                coverage_type = "coverage_inversed"
            else:
                coverage_type = "coverage_simple"
            feature = await db_client.get_reference_coverage(
                val["dataset_name_snake_case"], coverage_type
            )
            feature.properties.update(
                {"refernce_dataset": val["dataset_name_snake_case"]}
            )
            features.append(feature)
        return features

    @classmethod
    def attribution(cls) -> str:
        # TODO: add attribution
        return get_attribution(["OSM"])

    async def init(self) -> None:
        dataset_metadata = await load_datasets_metadata()
        for key, val in dataset_metadata.items():
            self.data_ref[key] = val
            self.area_cov[key] = None  # covered area [%]
            self.length_matched[key] = None
            self.length_total[key] = None
            self.length_osm[key] = None
            self.ratio[key] = None
            self.warnings[key] = None

    async def preprocess(self) -> None:
        for key, val in self.data_ref.items():
            # get area covered by reference dataset [%]
            self.area_cov[key] = await db_client.get_intersection_area(
                self.feature,
                val["dataset_name_snake_case"],
            )
            self.warnings[key] = self.check_major_edge_cases(key)
            if self.warnings[key] != "":
                continue

            # clip input geom with coverage of reference dataset
            feature = await db_client.get_intersection_geom(
                self.feature,
                val["dataset_name_snake_case"],
            )

            # get covered road length
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
        self.result.description = ""
        for key in self.data_ref.keys():
            # if major edge case present add to description
            # and continue with next dataset
            edge_case = self.check_major_edge_cases(key)
            if edge_case != "":
                self.result.description += edge_case + " "
                continue

            self.warnings[key] += self.check_minor_edge_cases(key)
            # ZeroDivisionError can not occur because of `check_major_edge_cases()`
            self.ratio[key] = self.length_matched[key] / self.length_total[key]

            self.result.description += self.warnings[key] + "\n"
            self.result.description += (
                f"{self.data_ref[key]['dataset_name']} has a road length of "
                f"{(self.length_total[key]/1000):.2f} km, of which "
                f"{(self.length_matched[key]/1000):.2f} km are covered by roads in "
                f"OSM. "
            )

        ratios = [v for v in self.ratio.values() if v is not None]
        if ratios:
            self.result.value = float(mean(ratios))

        if self.result.value is not None:
            if self.result.value >= self.th_high:
                self.result.class_ = 5
            elif self.th_high > self.result.value >= self.th_low:
                self.result.class_ = 3
            elif self.th_low > self.result.value >= 0:
                self.result.class_ = 1

        label_description = self.metadata.label_description[self.result.label]
        self.result.description += label_description
        # remove double white spaces
        self.result.description = " ".join(self.result.description.split())

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
            ref_name.append(self.data_ref[key]["dataset_name"])
            ref_color.append(Color[self.data_ref[key]["color"]].value)
            ref_processingdate.append(self.data_ref[key]["date"])
            ref_ratio.append(val)

        for i, (name, ratio, date) in enumerate(
            zip(ref_name, ref_ratio, ref_processingdate)
        ):
            fig.add_trace(
                pgo.Bar(
                    x=[name],
                    y=[ratio * 100],
                    name=f"{round((ratio * 100), 1)}% of {name} are matched by OSM",
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
                    name="{0}% of {1} are not matched by OSM".format(
                        round((100 - ratio * 100), 1),
                        name,
                    ),
                    marker=dict(
                        color="rgba(0,0,0,0)", line=dict(color="black", width=1)
                    ),
                    width=0.4,
                    hovertext=f"Not OSM Covered: {length_difference_km:.2f} km "
                    f"({date:%b %d, %Y})",
                    hoverinfo="text",
                    textposition="outside",
                )
            )

        fig.update_layout(
            barmode="stack",
            title="Road Comparison",
            yaxis=dict(title="Matched road length [%]"),
        )

        fig.update_layout(
            legend=dict(
                orientation="h",
                entrywidth=270,
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5,
            ),
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def check_major_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.area_cov[dataset] * 100
        if coverage is None or coverage == 0:
            return f"Reference dataset {dataset} does not cover area-of-interest. "
        elif coverage < 10:
            return (
                "Only {:.2f}% of the area-of-interest is covered ".format(coverage)
                + f"by the reference dataset ({dataset}). "
                + f"No quality estimation with reference {dataset} is possible."
            )
        elif self.length_total[dataset] == 0:
            return f"{dataset} does not contain roads for your area-of-interest. "
        else:
            return ""

    def check_minor_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.area_cov[dataset] * 100
        if coverage < 95:
            return (
                f"{dataset} does only cover {coverage:.2f}% of your area-of-interest. "
                "Comparison is made for the intersection area."
            )
        else:
            return ""

    def format_sources(self):
        sources = []
        for dataset_key, dataset_value in self.data_ref.items():
            if dataset_value["link"] is not None:
                sources.append(f"<a href='{dataset_value['link']}'>{dataset_key}</a>")
            else:
                sources.append(dataset_key)
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
                query.format(
                    table_name=table_name,
                ),
                (geom,),
            )
            res = await cur.fetchone()
    return res[0], res[1]


async def load_datasets_metadata() -> dict:
    """Load dataset metadata from the database."""
    dns = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("postgres_host"),
        port=get_config_value("postgres_port"),
        database=get_config_value("postgres_db"),
        user=get_config_value("postgres_user"),
        password=get_config_value("postgres_password"),
    )

    dataset_metadata = {}

    async with await psycopg.AsyncConnection.connect(dns) as con:
        async with con.cursor() as cur:
            await cur.execute(
                "SELECT * "
                "FROM comparison_indicators_metadata "
                "WHERE indicator = 'road_comparison';"
            )
            async for row in cur:
                dataset_name = row[0]
                dataset_name_snake_case = row[1]
                link = row[2]
                date = row[3]  # Convert date object to string
                description = row[4]
                color = row[5]
                table_name = row[6]
                dataset_metadata[dataset_name] = {
                    "dataset_name": dataset_name,
                    "dataset_name_snake_case": dataset_name_snake_case,
                    "link": link,
                    "date": date,
                    "description": description,
                    "color": color,
                    "table_name": table_name,
                }

    return dataset_metadata
