import json
import logging
import os
from string import Template

import geojson
import plotly.graph_objects as pgo
import psycopg
import yaml
from async_lru import alru_cache
from dateutil import parser
from geojson import Feature, MultiPolygon, Polygon
from numpy import mean

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.definitions import Color, get_attribution
from ohsome_quality_api.geodatabase import client as db_client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic


class BuildingComparison(BaseIndicator):
    def __init__(
        self,
        topic: BaseTopic,
        feature: Feature,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )
        self.area_osm: float | None = None
        self.area_references: dict = {}
        # The result is the ratio of area within coverage (between 0-1) or an empty list
        self.coverage: dict = {}

        # TODO: Evaluate thresholds
        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow
        self.above_one_th = 1.30

    @classmethod
    async def coverage(cls, inverse=False) -> Polygon | MultiPolygon:
        result = await db_client.get_eubucco_coverage(inverse)
        return geojson.loads(result[0]["geom"])

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "EUBUCCO"])

    async def preprocess(self) -> None:
        result = await db_client.get_eubucco_coverage_intersection_area(self.feature)
        if result:
            self.coverage["EUBUCCO"] = result[0]["area_ratio"]
        else:
            self.coverage["EUBUCCO"] = None
            return

        edge_case = self.check_major_edge_cases()
        if edge_case:
            self.result.description = edge_case
            return

        self.feature = await db_client.get_eubucco_coverage_intersection(self.feature)
        feature_string = json.dumps(self.feature)
        db_query_result = await get_eubucco_building_area(feature_string)
        self.area_references["EUBUCCO"] = db_query_result / (1000 * 1000)
        osm_query_result = await ohsome_client.query(
            self.topic,
            self.feature,
        )
        raw = osm_query_result["result"][0]["value"] or 0  # if None
        self.area_osm = raw / (1000 * 1000)
        self.result.timestamp_osm = parser.isoparse(
            osm_query_result["result"][0]["timestamp"]
        )

    def calculate(self) -> None:
        # TODO: put checks into check_corner_cases. Let result be undefined.
        if self.result.label == "undefined" and self.check_major_edge_cases():
            return
        if self.check_minor_edge_cases():
            self.result.description = self.check_minor_edge_cases()
        else:
            self.result.description = ""

        if all(v == 0 for v in self.area_references.values()):
            self.result.description += "Warning: No reference data in this area. "
            pass
        else:
            self.result.value = float(
                mean(
                    [self.area_osm / v for v in self.area_references.values() if v != 0]
                )
            )

        if self.result.value is None:
            return
        elif self.above_one_th >= self.result.value >= self.th_high:
            self.result.class_ = 5
        elif self.th_high > self.result.value >= self.th_low:
            self.result.class_ = 3
        elif self.th_low > self.result.value >= 0:
            self.result.class_ = 1
        elif self.result.value > self.above_one_th:
            # TODO: move this to edge_case functions
            self.result.description += (
                "Warning: Because of a big difference between OSM and the reference "
                + "data no quality estimation has been made. "
                + "It could be that the reference data is outdated. "
            )

        template = Template(self.metadata.result_description)
        self.result.description += template.substitute(
            ratio=round(self.result.value * 100, 2),
            coverage=round(self.coverage["EUBUCCO"] * 100, 2),
        )
        label_description = self.metadata.label_description[self.result.label]
        self.result.description += "\n" + label_description

    def create_figure(self) -> None:
        if self.result.label == "undefined" and self.check_major_edge_cases():
            logging.info(
                "Result is undefined and major edge case is present. "
                + "Skipping figure creation."
            )
            return
        fig = pgo.Figure()
        fig.add_trace(
            pgo.Bar(
                name="OSM",
                x=["OSM" + f" ({self.result.timestamp_osm:%b %d, %Y})"],
                y=[round(self.area_osm, 2)],
                marker_color=Color.GREEN.value,
            )
        )
        for name, area in self.area_references.items():
            fig.add_trace(
                pgo.Bar(
                    name=name,
                    x=[
                        f"{name} ({load_source_data(name)['date']})"
                        if load_source_data(name)["date"] is not None
                        else name
                    ],
                    y=[round(area, 2)],
                    marker_color=Color.PURPLE.value,
                )
            )

        fig.update_layout(title_text=("Building Comparison"), showlegend=True)
        fig.update_yaxes(title_text="Building Area [km²]")
        fig.update_xaxes(
            title_text="Reference Datasets ("
            + get_sources(self.area_references.keys())
            + ")"
        )
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def check_major_edge_cases(self) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.coverage["EUBUCCO"]
        if coverage is None or coverage == 0.00:
            return "Reference dataset does not cover area-of-interest."
        elif coverage < 0.10:
            return (
                "Only {:.2f}% of the area-of-interest is covered ".format(
                    coverage * 100
                )
                + "by the reference dataset (EUBUCCO). "
                + "No quality estimation is possible."
            )
        else:
            return ""

    def check_minor_edge_cases(self) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.coverage["EUBUCCO"]
        if coverage < 0.95:
            return (
                "Warning: Reference data does not cover the whole input geometry. "
                + "Input geometry is clipped to the coverage. Result is only calculated"
                " for the intersection area. "
            )
        else:
            return ""


@alru_cache
async def get_eubucco_building_area(feature_string: str) -> float:
    """Get the building area for a AoI from the EUBUCCO dataset."""
    # TODO: https://github.com/GIScience/ohsome-quality-api/issues/746
    file_path = os.path.join(db_client.WORKING_DIR, "select_building_area.sql")
    feature = json.loads(feature_string)
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(feature["geometry"])
    dns = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("postgres_host"),
        port=get_config_value("postgres_port"),
        database=get_config_value("postgres_db"),
        user=get_config_value("postgres_user"),
        password=get_config_value("postgres_password"),
    )
    async with await psycopg.AsyncConnection.connect(dns) as con:
        async with con.cursor() as cur:
            await cur.execute(query, (geom,))
            res = await cur.fetchone()
    return res[0] or 0.0


def get_sources(reference_datasets):
    sources = ""
    for dataset in reference_datasets:
        source_metadata = load_source_data(dataset)
        if source_metadata["link"] is not None:
            sources += f"<a href='{load_source_data(dataset)['link']}'>{dataset}</a>"
        else:
            sources += f"{dataset}"
    return sources


def load_source_data(reference_dataset) -> dict:
    file_path = os.path.join(os.path.dirname(__file__), "sources.yaml")

    with open(file_path, "r") as f:
        raw = yaml.safe_load(f)

    link = raw.get(reference_dataset, {}).get("link")
    date = raw.get(reference_dataset, {}).get("date")

    return {"link": link, "date": date}
