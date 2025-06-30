import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from string import Template

import geojson
import plotly.graph_objects as pgo
from geojson import Feature
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from ohsome_quality_api.api.request_models import (
    CorineLandCoverClass,
    CorineLandCoverClassLevel1,
)
from ohsome_quality_api.definitions import Color
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic as Topic

# Source: https://land.copernicus.eu/content/corine-land-cover-nomenclature-guidelines/docs/pdf/CLC2018_Nomenclature_illustrated_guide_20190510.pdf
# https://wiki.openstreetmap.org/wiki/Corine_Land_Cover
# Original colors of level 3 are mixed to get colors for level 2
# https://gradients.app/de/mix
clc_classes_level_2 = {
    CorineLandCoverClass("11"): {
        "name": "Urban fabric",
        "color": "#f30027",
    },
    CorineLandCoverClass("12"): {
        "name": "Industrial, commercial and transport units",
        "color": "#d979a9",
    },
    CorineLandCoverClass("13"): {
        "name": "Mine, dump and construction sites",
        "color": "#c43399",
    },
    CorineLandCoverClass("14"): {
        "name": "Artificial non-agricultural vegetated areas",
        "color": "#ffc6ff",
    },
    CorineLandCoverClass("21"): {"name": "Arable land", "color": "#f7f738"},
    CorineLandCoverClass("22"): {"name": "Permanent crops", "color": "#ea991a"},
    CorineLandCoverClass("23"): {"name": "Pastures", "color": "#e6e64d"},
    CorineLandCoverClass("24"): {
        "name": "Heterogeneous agricultural areas",
        "color": "#f6d97a",
    },
    CorineLandCoverClass("31"): {"name": "Forest", "color": "#44e100"},
    CorineLandCoverClass("32"): {
        "name": "Shrubs and/or herbaceous vegetation associations",
        "color": "#b0f247",
    },
    CorineLandCoverClass("33"): {
        "name": "Open spaces with little or no vegetation",
        "color": "#a1b8a8",
    },
    CorineLandCoverClass("41"): {"name": "Inland wetlands", "color": "#7a7aff"},
    CorineLandCoverClass("42"): {"name": "Coastal wetlands", "color": "#c8c8f7"},
    CorineLandCoverClass("51"): {"name": "Inland waters", "color": "#40dfec"},
    CorineLandCoverClass("52"): {"name": "Marine waters", "color": "#84fbd9"},
}
clc_classes_level_1 = {
    CorineLandCoverClassLevel1("1"): {"name": "Artificial areas"},
    CorineLandCoverClassLevel1("2"): {"name": "Agricultural areas"},
    CorineLandCoverClassLevel1("3"): {"name": "Forest and semi-natural areas"},
    CorineLandCoverClassLevel1("4"): {"name": "Wetlands"},
    CorineLandCoverClassLevel1("5"): {"name": "Water bodies"},
}


class LandCoverThematicAccuracy(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
        corine_land_cover_class: CorineLandCoverClass | None = None,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.clc_class = corine_land_cover_class
        self.timestamp_corine = datetime(2021, 1, 1, tzinfo=timezone.utc)

    @classmethod
    async def coverage(cls, inverse=False) -> list[Feature]:
        if inverse:
            query = (
                "SELECT ST_AsGeoJSON(inversed) FROM osm_corine_intersection_coverage"  # noqa
            )
        else:
            query = "SELECT ST_AsGeoJSON(simple) FROM osm_corine_intersection_coverage"
        result = await client.fetch(query)
        return [Feature(geometry=geojson.loads(result[0][0]))]

    async def preprocess(self) -> None:
        if self.clc_class:
            with open(Path(__file__).parent / "query-single-class.sql", "r") as file:
                query = file.read()
            results = await client.fetch(
                query, str(self.feature["geometry"]), int(self.clc_class.value)
            )
        else:
            with open(Path(__file__).parent / "query-multi-classes.sql", "r") as file:
                query = file.read()
            results = await client.fetch(query, str(self.feature["geometry"]))
        self.clc_classes_corine = [str(r["clc_class_corine"]) for r in results]
        self.clc_classes_osm = [str(r["clc_class_osm"]) for r in results]
        self.areas = [r["area"] / 1_000_000 for r in results]  # sqkm
        # TODO: take real timestamps from data
        self.result.timestamp_osm = datetime.now(timezone.utc)
        self.coverage_percent = await get_covered_area(self.feature)

    def calculate(self) -> None:
        if self.areas == []:
            return
        if self.clc_class:
            # single class
            self.clc_classes_osm = [
                "1" if clc_class_osm == self.clc_class.value else "0"
                for clc_class_osm in self.clc_classes_osm
            ]
            self.clc_classes_corine = [
                "1" if clc_class_corine == self.clc_class.value else "0"
                for clc_class_corine in self.clc_classes_corine
            ]
            self.f1_score = f1_score(
                self.clc_classes_corine,
                self.clc_classes_osm,
                average="binary",
                sample_weight=self.areas,
                labels=list(set(self.clc_classes_corine)),
                pos_label="1",
            )
            self.confusion_matrix_normalized = confusion_matrix(
                self.clc_classes_corine,
                self.clc_classes_osm,
                sample_weight=self.areas,
                normalize="all",
            ).tolist()
            self.confusion_matrix = confusion_matrix(
                self.clc_classes_corine,
                self.clc_classes_osm,
                sample_weight=self.areas,
            ).tolist()
        else:
            # multi/all classes
            self.f1_score = f1_score(
                self.clc_classes_corine,
                self.clc_classes_osm,
                average="micro",
                sample_weight=self.areas,
                labels=list(set(self.clc_classes_corine)),
            )
            (
                self.precision_scores,
                self.recall_scores,
                self.f1_scores,
                self.support_scores,
            ) = precision_recall_fscore_support(
                self.clc_classes_corine,
                self.clc_classes_osm,
                average=None,  # for each
                sample_weight=self.areas,
                # reverse for result figure
                labels=list(sorted(set(self.clc_classes_corine), reverse=True)),
            )

        # NOTE: For introspection/testing only
        # self.report = classification_report(
        #     self.clc_classes_corine,
        #     self.clc_classes_osm,
        #     sample_weight=self.areas,
        #     zero_division=numpy.nan,
        # )

        self.result.value = self.f1_score
        if self.f1_score > 0.9:
            self.result.class_ = 5
        elif self.f1_score > 0.6:
            self.result.class_ = 3
        else:
            self.result.class_ = 1

        template = Template(self.templates.label_description[self.result.label])
        if self.clc_class is None:
            clc_class = "all CORINE Land Cover (CLC) classes"
        else:
            clc_class = "CORINE Land Cover (CLC) class <em>{0}</em>".format(
                clc_classes_level_2[self.clc_class]["name"]
            )
        label_description = template.safe_substitute(
            {
                "f1_score": round(self.f1_score * 100, 2),
                "clc_class": clc_class,
            }
        )
        note = ""
        if self.coverage_percent != 100:
            note += (
                f"Warning: There is only {self.coverage_percent}% "
                f"coverage with the comparison data. "
            )
        note += (
            "Please take the Land Cover Completeness indicator into account for "
            + "interpretation of these results."
        )
        self.result.description = (
            f"{label_description} {self.templates.result_description} {note}"
        )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        if self.clc_class:
            self._create_figure_single_class()
        else:
            self._create_figure_multi_class()

    def _create_figure_multi_class(self):
        bars = []
        for i, clc_class in enumerate(
            # reverse for result figure
            list(sorted(set(self.clc_classes_corine), reverse=True))
        ):
            number_level_2 = CorineLandCoverClass(clc_class).value
            name_level_2 = "{0} {1}".format(
                f"{number_level_2[0]}.{number_level_2[1]}",
                clc_classes_level_2[CorineLandCoverClass(clc_class)]["name"],
            )
            color = (clc_classes_level_2[CorineLandCoverClass(clc_class)]["color"],)
            x = self.f1_scores[i] * 100
            y = name_level_2 + " "  # TODO: look at axis setting to create space
            area_percentage = self.support_scores[i] * 100 / sum(self.support_scores)
            bars.append(
                pgo.Bar(
                    name="",
                    x=[x],
                    y=[y],
                    orientation="h",
                    marker_color=color,
                    hovertemplate=(
                        f"Precision [%]: {(self.precision_scores[i] * 100):.2f}<br>"
                        f"Recall [%]: {(self.recall_scores[i] * 100):.2f}<br>"
                        f"Area [km<sup>2</sup>]: {self.support_scores[i]:.2f}<br>"
                        f"Area [%]: {(area_percentage):.2f}"
                    ),
                    text=f"{x:.2f}",
                    textposition="auto",
                )
            )
        fig = pgo.Figure(
            data=bars,
            layout=pgo.Layout(
                {
                    "autotypenumbers": "strict",
                    "xaxis": {"title": {"text": "F1-Score [%]"}, "range": [0, 100]},
                },
                showlegend=False,
            ),
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def _create_figure_single_class(self):
        name_level_2 = clc_classes_level_2[CorineLandCoverClass(self.clc_class.value)][
            "name"
        ]
        fig = pgo.Figure(
            # TODO: remove or grey out other_class x other_classes since its always 0%
            data=[
                pgo.Bar(
                    y=[1],
                    x=[self.confusion_matrix_normalized[1][0]],
                    width=[0.5],
                    orientation="h",
                    name="False Negative",  # e.g corine = forest | osm = other
                    marker_color="lightgrey",
                    texttemplate=f"{self.confusion_matrix_normalized[1][0]:.2%}",
                    textposition="inside",
                    hovertemplate=(
                        f"CORINE class: {name_level_2}<br>"
                        f"OSM class: Other<br>"
                        f"Area [km<sup>2</sup>]: {self.confusion_matrix[1][0]:.2f}<br>"
                        f"Area [%]: {self.confusion_matrix_normalized[1][0]:.2%}"
                    ),
                    legendrank=3,
                ),
                pgo.Bar(
                    y=[1],
                    x=[self.confusion_matrix_normalized[1][1]],
                    width=[0.5],
                    orientation="h",
                    name="True Positive",  # e.g. corine = forest | osm = forest
                    marker_color=Color.GREEN.value,
                    texttemplate=f"{self.confusion_matrix_normalized[1][1]:.2%}",
                    textposition="inside",
                    # textfont_color="black",
                    hovertemplate=(
                        f"CORINE class: {name_level_2}<br>"
                        f"OSM class: {name_level_2}<br>"
                        f"Area [km<sup>2</sup>]: {self.confusion_matrix[1][1]:.2f}<br>"
                        f"Area [%]: {self.confusion_matrix_normalized[1][1]:.2%}"
                    ),
                    legendrank=2,
                ),
                pgo.Bar(
                    y=[1],
                    x=[self.confusion_matrix_normalized[0][1]],
                    width=[0.5],
                    orientation="h",
                    name="False Positive",  # e.g. corine = other | osm = forest
                    marker_color=Color.GREY.value,
                    texttemplate=f"{self.confusion_matrix_normalized[0][1]:.2%}",
                    textposition="inside",
                    hovertemplate=(
                        f"CORINE class: Other<br>"
                        f"OSM class: {name_level_2}<br>"
                        f"Area [km<sup>2</sup>]: {self.confusion_matrix[0][1]:.2f}<br>"
                        f"Area [%]: {self.confusion_matrix_normalized[0][1]:.2%}"
                    ),
                    legendrank=1,
                ),
            ]
        )

        fig.update_layout(
            {
                "legend": {
                    "yanchor": "top",
                    "x": 0,
                    "y": 0.2,
                    "orientation": "h",
                }
            }
        )
        fig.update_layout(
            barmode="stack",
            plot_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw


async def get_covered_area(feature) -> float:
    query = """SELECT 100.0 * ST_Area(
            ST_Intersection(simple, ST_SetSRID(ST_GeomFromGeoJSON($1), 4326))
                              ) / NULLIF(
                ST_Area(ST_SetSRID(ST_GeomFromGeoJSON($1), 4326)), 0) AS
                      coverage_percent

           FROM osm_corine_intersection_coverage
           WHERE ST_Intersects(simple, ST_SetSRID(ST_GeomFromGeoJSON($1), 4326))
        """
    feature_geojson_str = json.dumps(feature["geometry"])
    result = await client.fetch(query, feature_geojson_str)
    return result[0][0]
