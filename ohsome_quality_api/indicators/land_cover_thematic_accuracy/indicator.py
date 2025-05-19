import logging
from datetime import datetime, timezone
from pathlib import Path
from string import Template

import numpy
import plotly.graph_objects as pgo
from geojson import Feature
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
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
clc_classes_level_2 = {
    CorineLandCoverClass("11"): "Urban fabric",
    CorineLandCoverClass("12"): "Industrial, commercial and transport units",
    CorineLandCoverClass("13"): "Mine, dump and construction sites",
    CorineLandCoverClass("14"): "Artificial non-agricultural vegetated areas",
    CorineLandCoverClass("21"): "Arable land",
    CorineLandCoverClass("22"): "Permanent crops",
    CorineLandCoverClass("23"): "Pastures",
    CorineLandCoverClass("24"): "Heterogeneous agricultural areas",
    CorineLandCoverClass("31"): "Forest",
    CorineLandCoverClass("32"): "Shrubs and/or herbaceous vegetation associations",
    CorineLandCoverClass("33"): "Open spaces with little or no vegetation",
    CorineLandCoverClass("41"): "Inland wetlands",
    CorineLandCoverClass("42"): "Coastal wetlands",
    CorineLandCoverClass("51"): "Inland waters",
    CorineLandCoverClass("52"): "Marine waters",
}
clc_classes_level_1 = {
    CorineLandCoverClassLevel1("1"): {
        "name": "Artificial areas",
        "color": Color["GREY"],
    },
    CorineLandCoverClassLevel1("2"): {
        "name": "Agricultural areas",
        "color": Color["YELLOW"],
    },
    CorineLandCoverClassLevel1("3"): {
        "name": "Forest and semi-natural areas",
        "color": Color["GREEN"],
    },
    CorineLandCoverClassLevel1("4"): {"name": "Wetlands", "color": Color["VIOLET"]},
    CorineLandCoverClassLevel1("5"): {"name": "Water bodies", "color": Color["BLUE"]},
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
        self.timestamp_corine = datetime.now(timezone.utc)

    def calculate(self) -> None:
        if self.clc_class:
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
            average="weighted",
            sample_weight=self.areas,
            labels=list(set(self.clc_classes_corine)),
        )
        self.f1_scores = f1_score(
            self.clc_classes_corine,
            self.clc_classes_osm,
            average=None,  # for each
            sample_weight=self.areas,
            labels=list(sorted(set(self.clc_classes_corine))),
        )

        self.precision_scores = precision_score(
            self.clc_classes_corine,
            self.clc_classes_osm,
            average=None,  # for each
            sample_weight=self.areas,
            labels=list(sorted(set(self.clc_classes_corine))),
        )

        self.recall_scores = recall_score(
            self.clc_classes_corine,
            self.clc_classes_osm,
            average=None,  # for each
            sample_weight=self.areas,
            labels=list(sorted(set(self.clc_classes_corine))),
        )

        self.confusion_matrix = confusion_matrix(
            self.clc_classes_corine,
            self.clc_classes_osm,
            sample_weight=self.areas,
            normalize="all",
        )
        self.result.value = self.f1_score
        # TODO: re-evaluate thresholds
        if self.f1_score > 0.8:
            self.result.class_ = 5
        elif self.f1_score > 0.5:
            self.result.class_ = 3
        else:
            self.result.class_ = 1

        template = Template(self.templates.label_description[self.result.label])
        if self.clc_class is None:
            clc_class = "all CLC classes"
        else:
            clc_class = "CLC class <em>{0}</em>".format(
                clc_classes_level_2[self.clc_class]
            )
        label_description = template.safe_substitute(
            {
                "f1_score": round(self.f1_score * 100, 2),
                "clc_class": clc_class,
            }
        )
        self.result.description = (
            f"{label_description} {self.templates.result_description}"
        )

        # NOTE: For introspection/testing only
        self.report = classification_report(
            self.clc_classes_corine,
            self.clc_classes_osm,
            sample_weight=self.areas,
            zero_division=numpy.nan,
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
        for i, clc_class in enumerate(list(sorted(set(self.clc_classes_corine)))):
            clc_class_level_1 = CorineLandCoverClassLevel1(clc_class[0])
            color = clc_classes_level_1[clc_class_level_1]["color"].value
            name_level_1 = clc_classes_level_1[clc_class_level_1]["name"]
            number_level_2 = CorineLandCoverClass(clc_class).value
            name_level_2 = "{0} {1}".format(
                number_level_2,
                clc_classes_level_2[CorineLandCoverClass(clc_class)],
            )
            x = clc_class
            y = self.f1_scores[i] * 100
            bars.append(
                pgo.Bar(
                    name=name_level_2,
                    x=[x],
                    y=[y],
                    legendgroup=name_level_1,
                    legendgrouptitle_text=name_level_1,
                    marker_color=color,
                    hovertemplate=(
                        f"Precision: {self.precision_scores[i]:.2f}<br>"
                        f"Recall: {self.recall_scores[i]:.2f}"
                    ),
                )
            )
        fig = pgo.Figure(
            # TODO: add precision/recall as hover interaction
            # TODO: use semantic UI colors
            data=bars,
            layout=pgo.Layout(
                {
                    "autotypenumbers": "strict",
                    "legend": {
                        "yanchor": "top",
                        "x": 0,
                        "y": -0.5,
                        "orientation": "h",
                    },
                    "xaxis": {
                        "title": {"text": "CORINE Land Cover Class (CLC Class)"},
                        "dtick": 1,
                    },
                    "yaxis": {"title": {"text": "F1-Score [%]"}, "range": [0, 100]},
                },
                showlegend=True,
            ),
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def _create_figure_single_class(self):
        clc_class_level_1 = CorineLandCoverClassLevel1(self.clc_class.value[0])
        name_level_1 = clc_classes_level_1[clc_class_level_1]["name"]
        name_level_2 = clc_classes_level_2[CorineLandCoverClass(self.clc_class.value)]
        class_name = name_level_1 + " <br> " + name_level_2
        class_labels = ["Other classes", class_name]
        fig = pgo.Figure(
            # TODO: remove or grey out other_class x other_classes since its always 0%
            data=pgo.Heatmap(
                z=self.confusion_matrix,
                x=class_labels,
                y=class_labels,
                text=self.confusion_matrix,
                texttemplate="%{text:.2%}",
                colorscale="Viridis",
                colorbar=dict(title="Proportion"),
                hovertemplate="Predicted: %{x}<br>Actual: %{y}<br>"
                "Value: %{z:.2%}<extra></extra>",
            )
        )

        fig.update_layout(
            xaxis=dict(
                title="Corine Land Cover Class in OSM",
                ticktext=class_labels,
            ),
            yaxis=dict(
                title="Corine Land Cover Class (actual)",
                ticktext=class_labels,
            ),
        )
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
