import logging
import os
from functools import cache
from string import Template

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
        # The result is the ratio of area within coverage (between 0-1) or an empty list
        #
        # TODO: Evaluate thresholds
        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow
        self.above_one_th = 1.30

        self.data_ref: dict[str, dict] = {}
        self.area_osm: dict[str, float | None] = {}
        self.area_ref: dict[str, float | None] = {}
        self.area_cov: dict[str, float | None] = {}
        self.ratio: dict[str, float | None] = {}
        # self.data_ref: list = load_reference_datasets()  # reference datasets
        for key, val in load_datasets_metadata().items():
            self.data_ref[key] = val
            self.area_osm[key] = None  # osm building area
            self.area_ref[key] = None  # reference building area [sqkm]
            self.area_cov[key] = None  # covered area [%]
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
        return get_attribution(["OSM", "EUBUCCO", "Microsoft Buildings"])

    async def preprocess(self) -> None:
        for key, val in self.data_ref.items():
            # get coverage [%]
            self.area_cov[key] = await db_client.get_intersection_area(
                self.feature,
                val["coverage"]["simple"],
            )

            if self.check_major_edge_cases(key):
                continue

            # clip input geom with coverage of reference dataset
            feature = await db_client.get_intersection_geom(
                self.feature,
                val["coverage"]["simple"],
            )

            # get reference building area
            result = await get_reference_building_area(feature, key)
            self.area_ref[key] = result / (1000 * 1000)

            # get osm building area
            result = await ohsome_client.query(self.topic, feature)
            value = result["result"][0]["value"] or 0.0  # if None
            self.area_osm[key] = value / (1000 * 1000)
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
        self.result.description = "".join(edge_cases)

        for key in self.data_ref.keys():
            # if None in (self.ratio[key], self.area_cov[key], self.data_ref[key]):
            if self.check_major_edge_cases(key):
                continue

            self.result.description += self.check_minor_edge_cases(key)
            # TODO: check for None explicitly?
            # TODO: add warning for user, that no buildings are present?
            try:
                self.ratio[key] = self.area_osm[key] / self.area_ref[key]
            except ZeroDivisionError:
                self.ratio[key] = 0.0

            template = Template(self.metadata.result_description)
            self.result.description += template.substitute(
                ratio=round(self.ratio[key] * 100, 2),
                coverage=round(self.area_cov[key] * 100, 2),
                dataset=self.data_ref[key]["name"],
            )

        ratios = [v for v in self.ratio.values() if v is not None]
        ratios = [v for v in ratios if v <= self.above_one_th]
        if ratios:
            self.result.value = float(mean(ratios))
        else:
            self.result.description += (
                "Warning: OSM has substantivly more buildings mapped than the Reference"
                + " datasets. No quality estimation has been made."
            )

        if self.result.value is not None:
            if self.above_one_th >= self.result.value >= self.th_high:
                self.result.class_ = 5
            elif self.th_high > self.result.value >= self.th_low:
                self.result.class_ = 3
            elif self.th_low > self.result.value >= 0:
                self.result.class_ = 1

        label_description = self.metadata.label_description[self.result.label]
        self.result.description += "\n" + label_description

    def create_figure(self) -> None:
        edge_cases = [self.check_major_edge_cases(k) for k in self.data_ref.keys()]
        if self.result.label == "undefined" and all(edge_cases):
            logging.info(
                "Result is undefined and major edge case is present."
                " Skipping figure creation."
            )
            return

        ref_data = []
        ref_x = []
        ref_y = []
        osm_x = []
        osm_y = []
        ref_hover = []
        osm_hover = []
        ref_color = []
        for key, dataset in self.data_ref.items():
            if None in (self.area_ref[key], self.area_osm[key]):
                continue
            ref_x.append(dataset["name"])
            ref_y.append(round(self.area_ref[key], 2))
            ref_data.append(dataset)
            osm_x.append(dataset["name"])
            osm_y.append(round(self.area_osm[key], 2))
            ref_hover.append(f"{dataset['name']} ({dataset['date']})")
            osm_hover.append(f"OSM ({self.result.timestamp_osm:%b %d, %Y})")
            ref_color.append(Color[dataset["color"]].value)

        fig = pgo.Figure(
            data=[
                pgo.Bar(
                    name="OSM building area",
                    x=osm_x,
                    y=osm_y,
                    marker_color=Color.GREEN.value,
                    hovertext=osm_hover,
                ),
                pgo.Bar(
                    name=ref_x[0],
                    x=ref_x,
                    y=ref_y,
                    marker_color=ref_color,
                    hovertext=ref_hover,
                    legendgroup="Reference",
                ),
            ]
        )

        # Put every reference dataset to legend by adding transparent shapes
        for dataset in list(self.data_ref.values())[1:]:
            fig.add_shape(
                name=dataset["name"],
                legendgroup="Reference",
                showlegend=True,
                type="rect",
                layer="below",
                line=dict(width=0),
                fillcolor=Color[dataset["color"]].value,
                x0=0,
                y0=0,
                x1=0,
                y1=0,
            )

        layout = {
            "title_text": "Building Comparison",
            "showlegend": True,
            "barmode": "group",
            "yaxis_title": "Building Area [km²]",
            "xaxis_title": f"Reference Datasets ({self.format_sources()})",
        }
        fig.update_layout(**layout)

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


@alru_cache
async def get_reference_building_area(feature: Feature, table_name: str) -> float:
    """Get the building area for a AoI from the EUBUCCO dataset."""
    # TODO: https://github.com/GIScience/ohsome-quality-api/issues/746
    file_path = os.path.join(db_client.WORKING_DIR, "select_building_area.sql")
    with open(file_path, "r") as file:
        query = file.read()
    dns = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("postgres_host"),
        port=get_config_value("postgres_port"),
        database=get_config_value("postgres_db"),
        user=get_config_value("postgres_user"),
        password=get_config_value("postgres_password"),
    )
    table_name = table_name.replace(" ", "_")
    geom = geojson.dumps(feature.geometry)
    async with await psycopg.AsyncConnection.connect(dns) as con:
        async with con.cursor() as cur:
            await cur.execute(query.format(table_name=table_name), (geom,))
            res = await cur.fetchone()
    return res[0] or 0.0


@cache
def load_datasets_metadata() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
