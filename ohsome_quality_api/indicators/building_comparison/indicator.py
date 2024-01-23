import logging
import os
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
        self.reference_datasets = load_reference_datasets()
        self.area_osm: dict = {}
        self.area_ref: dict = {}  # reference
        # The result is the ratio of area within coverage (between 0-1) or an empty list
        self.coverage: dict = {}

        # TODO: Evaluate thresholds
        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow
        self.above_one_th = 1.30

        self.coverage_intersections = {}

    @classmethod
    async def coverage(cls, inverse=False) -> list[Feature]:
        reference_datasets = load_reference_datasets()
        coverage_names = load_datasets_coverage_names(reference_datasets)
        result = await db_client.get_reference_coverage(coverage_names, inverse)
        features = []
        for i in range(len(result)):
            geom = geojson.loads(result[i])
            feature = geojson.Feature(geometry=geom, properties={})
            feature["properties"]["reference_dataset"] = reference_datasets[i]
            features.append(feature)
        return features

    # TODO
    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "EUBUCCO"])

    async def preprocess(self) -> None:
        major_edgecases = []
        for dataset in self.reference_datasets:
            # get coverage
            coverage_name = load_datasets_coverage_names([dataset])[0] + "_simple"
            result = await db_client.get_reference_coverage_intersection_area(
                self.feature, coverage_name
            )
            if result:
                self.coverage[dataset] = result[0]["area_ratio"]
            else:
                self.coverage[dataset] = None

            edge_case = self.check_major_edge_cases(dataset)
            if edge_case:
                major_edgecases.append(edge_case)
                continue

            self.coverage_intersections[
                dataset
            ] = await db_client.get_reference_coverage_intersection(
                self.feature, coverage_name
            )
            self.area_ref[dataset] = await get_reference_building_area(
                geojson.dumps(self.coverage_intersections[dataset]), dataset
            ) / (1000 * 1000)

            # get osm data for covered area
            osm_query_result = await ohsome_client.query(
                self.topic,
                self.coverage_intersections[dataset],
            )
            raw = osm_query_result["result"][0]["value"] or 0  # if None
            self.area_osm[dataset] = raw / (1000 * 1000)
            self.result.timestamp_osm = parser.isoparse(
                osm_query_result["result"][0]["timestamp"]
            )
        if len(major_edgecases) == len(self.reference_datasets):
            self.result.description += (
                " None of the reference datasets covers the area-of-interest."
            )
        elif len(major_edgecases) > 0:
            self.result.description = "".join(major_edgecases)
        elif len(major_edgecases) == 0:
            self.result.description = ""

    def calculate(self) -> None:
        # TODO: put checks into check_corner_cases. Let result be undefined.
        if self.result.label == "undefined" and all(
            self.check_major_edge_cases(dataset) for dataset in self.reference_datasets
        ):
            return

        for dataset in self.reference_datasets:
            if not self.check_major_edge_cases(dataset):
                self.result.description += self.check_minor_edge_cases(dataset)

        self.result.value, valid_refs_values = self.get_result_value()

        if self.result.value is not None:
            if self.above_one_th >= self.result.value >= self.th_high:
                self.result.class_ = 5
            elif self.th_high > self.result.value >= self.th_low:
                self.result.class_ = 3
            elif self.th_low > self.result.value >= 0:
                self.result.class_ = 1

            for ref in valid_refs_values.keys():
                template = Template(self.metadata.result_description)
                self.result.description += template.substitute(
                    ratio=round(valid_refs_values[ref] * 100, 2),
                    coverage=round(self.coverage[ref] * 100, 2),
                    dataset=ref,
                )

        label_description = self.metadata.label_description[self.result.label]
        self.result.description += "\n" + label_description

    def create_figure(self) -> None:
        if self.result.label == "undefined" and all(
            self.check_major_edge_cases(dataset) for dataset in self.reference_datasets
        ):
            logging.info(
                "Result is undefined and major edge case is present."
                " Skipping figure creation."
            )
            return

        hovertext_osm = [
            f"OSM ({self.result.timestamp_osm:%b %d, %Y})"
            for _ in self.reference_datasets
        ]

        reference_data = [
            (
                dataset,
                round(self.area_ref[dataset], 2),
                load_datasets_metadata(dataset),
            )
            for dataset in self.reference_datasets
        ]

        x_osm, y_osm = (
            self.reference_datasets,
            [round(self.area_osm[dataset], 2) for dataset in self.reference_datasets],
        )
        hovertext_reference = [
            f"{metadata['name']} ({metadata['date']})"
            if metadata["date"] is not None
            else dataset
            for dataset, _, metadata in reference_data
        ]
        colors_references = [
            Color[metadata["color"]].value for _, _, metadata in reference_data
        ]

        fig = pgo.Figure(
            data=[
                pgo.Bar(
                    name="OSM",
                    x=x_osm,
                    y=y_osm,
                    marker_color=Color.GREEN.value,
                    hovertext=hovertext_osm,
                ),
                pgo.Bar(
                    name=self.reference_datasets[0],
                    x=self.reference_datasets,
                    y=[item[1] for item in reference_data],
                    marker_color=colors_references,
                    hovertext=hovertext_reference,
                    legendgroup="Reference",
                ),
            ]
        )
        for dataset in self.reference_datasets[1:]:
            fig.add_shape(
                name=dataset,
                legendgroup="Reference",
                showlegend=True,
                type="rect",
                layer="below",
                line=dict(width=0),
                fillcolor=Color[load_datasets_metadata(dataset)["color"]].value,
                x0=0,
                y0=0,
                x1=0,
                y1=0,
            )

        layout_update = {
            "title_text": "Building Comparison",
            "showlegend": True,
            "barmode": "group",
            "yaxis_title": "Building Area [km²]",
            "xaxis_title": f"Reference Datasets ("
            f"{get_sources(self.area_ref.keys())}"
            f")",
        }

        fig.update_layout(**layout_update)

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def check_major_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.coverage[dataset]
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
        coverage = self.coverage[dataset]
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

    def get_result_value(self):
        if all(v == 0 for v in self.area_ref.values()):
            self.result.description += "Warning: No reference data in this area. "
            return None, None
        else:
            valid_references = [
                dataset
                for dataset in self.reference_datasets
                if dataset in self.area_ref
            ]

            for dataset in valid_references:
                self.result.description += (
                    f"Warning: No buildings in reference data {dataset} in this area. "
                    if self.area_ref[dataset] == 0
                    else ""
                )

            result_values = {
                dataset: self.area_osm[dataset] / self.area_ref[dataset]
                for dataset in valid_references
            }

            if all(value > self.above_one_th for value in result_values.values()):
                self.result.description += (
                    "Warning: Because of a big difference between OSM and the reference"
                    " in all reference"
                    " data. No quality estimation will be calculated. "
                )
                return None, None
            else:
                for dataset, value in result_values.items():
                    if value > self.above_one_th:
                        self.result.description += (
                            f"Warning: Because of a big difference between OSM and the"
                            f" reference dataset {dataset}, this data is not considered"
                            f" in the overall result value. "
                        )

                result_values_in_threshold = {
                    dataset: value
                    for dataset, value in result_values.items()
                    if value <= self.above_one_th
                }
                return (
                    mean(list(result_values_in_threshold.values())),
                    result_values_in_threshold,
                )


@alru_cache
async def get_reference_building_area(bpoly: str, table_name: str) -> float:
    """Get the building area for a AoI from the EUBUCCO dataset."""
    # TODO: https://github.com/GIScience/ohsome-quality-api/issues/746
    bpoly = geojson.loads(bpoly)
    file_path = os.path.join(db_client.WORKING_DIR, "select_building_area.sql")
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(bpoly.geometry)
    dns = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("postgres_host"),
        port=get_config_value("postgres_port"),
        database=get_config_value("postgres_db"),
        user=get_config_value("postgres_user"),
        password=get_config_value("postgres_password"),
    )
    table_name = table_name.replace(" ", "_")
    async with await psycopg.AsyncConnection.connect(dns) as con:
        async with con.cursor() as cur:
            await cur.execute(query.format(table_name=table_name), (geom,))
            res = await cur.fetchone()
    return res[0] or 0.0


def get_sources(reference_datasets):
    sources = []
    for dataset in reference_datasets:
        source_metadata = load_datasets_metadata(dataset)
        if source_metadata["link"] is not None:
            sources.append(
                f"<a href='{load_datasets_metadata(dataset)['link']}'>"
                f"{load_datasets_metadata(dataset)['name']}</a>"
            )
        else:
            sources.append(f"{dataset}")

    result = ", ".join(sources)
    return result


def load_datasets_metadata(reference_dataset) -> dict:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")

    with open(file_path, "r") as f:
        raw = yaml.safe_load(f)

    name = raw.get(reference_dataset, {}).get("name")
    link = raw.get(reference_dataset, {}).get("link")
    date = raw.get(reference_dataset, {}).get("date")
    color = raw.get(reference_dataset, {}).get("color")

    return {"name": name, "link": link, "date": date, "color": color}


def load_datasets_coverage_names(reference_datasets) -> list:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")

    with open(file_path, "r") as f:
        raw = yaml.safe_load(f)

    coverage_names = []
    for dataset in reference_datasets:
        coverage_names.append(raw.get(dataset, {}).get("coverage_name"))

    return coverage_names


def load_reference_datasets() -> list:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")

    with open(file_path, "r") as f:
        raw = yaml.safe_load(f)

    return list(raw.keys())
