import logging
import os
from pathlib import Path
from string import Template

import geojson
import plotly.graph_objects as pgo
import yaml
from dateutil import parser
from geojson import Feature
from numpy import mean

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
            if self.check_major_edge_cases(key) != "":
                continue

            # clip input geom with coverage of reference dataset
            feature = await db_client.get_intersection_geom(
                self.feature,
                val["coverage"]["simple"],
            )

            # get reference building area
            result = await get_reference_building_area(
                geojson.dumps(feature), val["table_name"]
            )
            self.area_ref[key] = result / (1000 * 1000)

            # get osm building area
            result = await ohsome_client.query(self.topic, feature)
            value = result["result"][0]["value"] or 0.0  # if None
            self.area_osm[key] = value / (1000 * 1000)
            timestamp = result["result"][0]["timestamp"]
            self.result.timestamp_osm = parser.isoparse(timestamp)

    def calculate(self) -> None:
        major_edge_case: bool = False
        result_description: str = ""
        for key in self.data_ref.keys():
            # if major edge case present add to description
            # and continue with next dataset
            edge_case = self.check_major_edge_cases(key)
            if edge_case != "":
                result_description = " ".join((result_description, edge_case))
                major_edge_case = True
                continue
            edge_case = self.check_minor_edge_cases(key)
            # ZeroDivisionError can not occur because of `check_major_edge_cases()`
            self.ratio[key] = self.area_osm[key] / self.area_ref[key]
            template = Template(self.templates.result_description)
            description = template.substitute(
                ratio=round(self.ratio[key] * 100, 2),
                coverage=round(self.area_cov[key] * 100, 2),
                dataset=self.data_ref[key]["name"],
            )
            result_description = " ".join((result_description, edge_case, description))

        ratios = [
            v for v in self.ratio.values() if v is not None and v <= self.above_one_th
        ]
        if ratios:
            self.result.value = float(mean(ratios))
            if self.above_one_th >= self.result.value >= self.th_high:
                self.result.class_ = 5
            elif self.th_high > self.result.value >= self.th_low:
                self.result.class_ = 3
            elif self.th_low > self.result.value >= 0:
                self.result.class_ = 1
            label_description = self.templates.label_description[self.result.label]
            self.result.description = " ".join((label_description, result_description))
        elif major_edge_case:
            label_description = self.templates.label_description[self.result.label]
            self.result.description = " ".join((label_description, result_description))
        else:
            label_description = self.templates.label_description[self.result.label]
            edge_case = (
                "OSM has substantivly more buildings than the reference datasets. The "
                "reference dataset is likely to miss many buildings."
            )
            self.result.description = " ".join(
                [label_description, edge_case, result_description]
            )
        # remove double white spaces
        self.result.description = " ".join(self.result.description.split())

    def create_figure(self) -> None:
        edge_cases = [self.check_major_edge_cases(k) for k in self.data_ref.keys()]
        if self.result.label == "undefined" and all(edge_cases):
            logging.info(
                "Result is undefined and major edge case is present. "
                "Skipping figure creation."
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
        osm_area = []
        ref_area = []
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
            osm_area.append(round(self.area_osm[key], 2))
            ref_area.append(round(self.area_ref[key], 2))

        fig = pgo.Figure(
            data=[
                pgo.Bar(
                    name="OSM building area"
                    + " ("
                    + " km², ".join(map(str, osm_area))
                    + " km²)",
                    x=osm_x,
                    y=osm_y,
                    marker_color=Color.GREY.value,
                    hovertext=osm_hover,
                    hoverinfo="text",
                ),
                pgo.Bar(
                    name=ref_x[0] + f" ({ref_area[0]} km²)",
                    x=ref_x,
                    y=ref_y,
                    marker_color=ref_color,
                    hovertext=ref_hover,
                    hoverinfo="text",
                    legendgroup="Reference",
                ),
            ]
        )
        for name, area, color in zip(ref_x[1:], ref_area[1:], ref_color[1:]):
            fig.add_shape(
                name=name + f" ({area} km²)",
                legendgroup="Reference",
                showlegend=True,
                type="rect",
                layer="below",
                line=dict(width=0),
                fillcolor=color,
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
            "legend": dict(
                orientation="h",
                entrywidth=270,
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5,
            ),
        }
        fig.update_layout(**layout)

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def check_major_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.area_cov[dataset] * 100
        if coverage is None or coverage == 0:
            return "{} does not cover your area-of-interest.".format(dataset)
        elif coverage < 10:
            return "Only {:.2f}% of your area-of-interest is covered by {}".format(
                coverage,
                dataset,
            )
        elif self.area_ref[dataset] == 0:
            return f"{dataset} does not contain buildings for your area-of-interest."
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
        for dataset in self.data_ref.values():
            if dataset["link"] is not None:
                sources.append(f"<a href='{dataset['link']}'>{dataset['name']}</a>")
            else:
                sources.append(f"{dataset}")
        result = ", ".join(sources)
        return result


# alru needs hashable type, therefore, use string instead of Feature
# @alru_cache
async def get_reference_building_area(feature_str: str, table_name: str) -> float:
    path = Path(__file__).parent / "query.sql"
    with open(path, "r") as file:
        query = file.read()
    feature = geojson.loads(feature_str)
    geom = geojson.dumps(feature.geometry)
    results = await db_client.fetch(
        query.format(table_name=table_name),
        geom,
    )
    return results[0][0] or 0.0


def load_datasets_metadata() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
