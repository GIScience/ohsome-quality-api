import logging
from string import Template

import geojson
import plotly.graph_objects as pgo
from dateutil import parser
from geojson import Feature, MultiPolygon, Polygon
from numpy import mean

from ohsome_quality_api.definitions import Color, get_attribution
from ohsome_quality_api.geodatabase import client as db_client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic

SOURCE_LINKS = {
    "EUBUCCO": "https://docs.eubucco.com/",
}


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
    async def coverage(cls) -> Polygon | MultiPolygon:
        result = await db_client.get_eubucco_coverage()
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
        if not self.check_major_edge_cases():
            self.feature = await db_client.get_eubucco_coverage_intersection(
                self.feature
            )
            db_query_result = await db_client.get_building_area(self.feature)
            raw = db_query_result[0]["area"] or 0
            self.area_references["EUBUCCO"] = raw / (1000 * 1000)

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
        if not self.result.description == "":
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
            self.result.description += (
                "Warning: No quality estimation made. "
                "OSM and reference data differ. Reference data is likely outdated. "
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
            logging.info("Result is undefined. Skipping figure creation.")
            return
        fig = pgo.Figure()
        fig.add_trace(
            pgo.Bar(
                name="OSM",
                x=["OSM"],
                y=[round(self.area_osm, 2)],
                marker_color=Color.GREEN.value,
            )
        )
        for name, area in self.area_references.items():
            fig.add_trace(
                pgo.Bar(
                    name=name,
                    x=[name],
                    y=[round(area, 2)],
                    marker_color=Color.PURPLE.value,
                )
            )

        fig.update_layout(title_text=("Building Comparison"), showlegend=True)
        fig.update_yaxes(title_text="Building Area [km²]")
        fig.update_xaxes(
            title_text="Datasets (" + get_sources(self.area_references.keys()) + ")"
        )
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def check_major_edge_cases(self) -> bool:
        coverage = self.coverage["EUBUCCO"]
        # TODO: generalize function
        if coverage is None or coverage == 0.00:
            self.result.description = (
                "Reference dataset does not cover area-of-interest."
            )
            return True
        elif coverage < 0.10:
            self.result.description = (
                "Only {:.2f}% of the area-of-interest is covered ".format(
                    coverage * 100
                )
                + "by the reference dataset (EUBUCCO). "
                + "No quality estimation is possible."
            )
            return True
        else:
            self.result.description = ""
            return False

    def check_minor_edge_cases(self) -> str:
        coverage = self.coverage["EUBUCCO"]
        if coverage < 0.95:
            return (
                "Warning: Reference data does not cover the whole input geometry. "
                + "Input geometry is clipped to the coverage. Result is only calculated"
                " for the intersection area. "
            )
        else:
            return ""


def get_sources(reference_datasets):
    sources = ""
    for dataset in reference_datasets:
        if dataset in SOURCE_LINKS.keys():
            sources += f"<a href='{SOURCE_LINKS[dataset]}'>{dataset}</a>"
    return sources
