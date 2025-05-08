import logging
from datetime import datetime, timezone
from pathlib import Path
from string import Template

import plotly.graph_objects as pgo
from geojson import Feature
from sklearn.metrics import classification_report, confusion_matrix, f1_score

from ohsome_quality_api.api.request_models import (
    CorineLandCoverClass,
    CorineLandCoverClassLevel1,
)
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic as Topic

# Source: https://land.copernicus.eu/content/corine-land-cover-nomenclature-guidelines/docs/pdf/CLC2018_Nomenclature_illustrated_guide_20190510.pdf
corine_classes = {
    CorineLandCoverClass(11): "Urban fabric",
    CorineLandCoverClass(12): "Industrial, commercial and transport units",
    CorineLandCoverClass(13): "Mine, dump and construction sites",
    CorineLandCoverClass(14): "Artificial non-agricultural vegetated areas",
    CorineLandCoverClass(21): "Arable land",
    CorineLandCoverClass(22): "Permanetn crops",
    CorineLandCoverClass(23): "Pastures",
    CorineLandCoverClass(24): "Heterogeneous agricultural areas",
    CorineLandCoverClass(31): "Forest",
    CorineLandCoverClass(32): "Shrubs and/or herbaceous vegetation associations",
    CorineLandCoverClass(33): "Open spaces with little or no vegetation",
    CorineLandCoverClass(41): "Inland wetlands",
    CorineLandCoverClass(42): "Coastal wetlands",
    CorineLandCoverClass(51): "Inland waters",
    CorineLandCoverClass(52): "Marine waters",
}
corine_top_level_class = {
    1: "Artificial areas",
    2: "Agricultural areas",
    3: "Forest and semi-natural areas",
    4: "Wetlands",
    5: "Water bodies",
}


class LandCoverThematicAccuracy(BaseIndicator):
    """
    TODO

    Only shows class for which OSM has data.

    Ergänzend zu dem Corine Completeness Indicator
    """

    def __init__(self, topic: Topic, feature: Feature, corine_class=None) -> None:
        super().__init__(topic=topic, feature=feature)
        self.corine_class = corine_class

    async def preprocess(self) -> None:
        if self.corine_class:
            with open(Path(__file__).parent / "query-single-class.sql", "r") as file:
                query = file.read()
            results = await client.fetch(
                query, str(self.feature["geometry"]), self.corine_class
            )
        else:
            with open(Path(__file__).parent / "query-all-classes.sql", "r") as file:
                query = file.read()
            results = await client.fetch(query, str(self.feature["geometry"]))
        self.clc_classes_corine = [r["clc_class_corine"] for r in results]
        self.clc_classes_osm = [r["clc_class_osm"] for r in results]
        self.areas = [r["area"] / 1_000_000 for r in results]  # sqkm
        # TODO: take real timestamps from data
        self.result.timestamp_osm = datetime.now(timezone.utc)
        self.timestamp_corine = datetime.now(timezone.utc)

    def calculate(self) -> None:
        if self.corine_class:
            self.clc_classes_osm = [
                1 if clc_class == CorineClass(self.corine_class).value else 0
                for clc_class in self.clc_classes_osm
            ]
            self.clc_classes_corine = [
                1 if clc_class == CorineClass(self.corine_class).value else 0
                for clc_class in self.clc_classes_corine
            ]

        self.f1_score = f1_score(
            self.clc_classes_corine,
            self.clc_classes_osm,
            average="weighted",
            sample_weight=self.areas,
            labels=list(set(self.clc_classes_corine)),
        )
        self.confusion_matrix = confusion_matrix(
            self.clc_classes_corine,
            self.clc_classes_osm,
            sample_weight=self.areas,
            normalize="all",
        )
        self.result.value = self.f1_score
        if self.f1_score > 0.8:
            self.result.class_ = 5
        elif self.f1_score > 0.5:
            self.result.class_ = 3
        else:
            self.result.class_ = 1

        template = Template(self.templates.result_description)
        description = template.substitute(
            score=round(self.f1_score * 100, 2),
        )
        self.result.description = " ".join(
            (description, self.templates.label_description[self.result.label])
        )

        # TODO: UdefinedMetricWarning
        # Recall is ill-defined and being set to 0.0 in labels with no
        # true samples. Use `zero_division` parameter to control this
        # behavior.
        self.report = classification_report(
            self.clc_classes_corine,
            self.clc_classes_osm,
            sample_weight=self.areas,
        )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        if self.corine_class:
            self._create_figure_single_class()
        else:
            self._create_figure_multi_class()

    def _create_figure_multi_class(self):
        self.f1_scores = f1_score(
            self.clc_classes_corine,
            self.clc_classes_osm,
            average=None,  # for each
            sample_weight=self.areas,
            labels=list(set(self.clc_classes_corine)),
        )
        class_labels = []
        for c in self.clc_classes_corine:
            class_labels.append(corine_classes[CorineLandCoverClass(c)])

        bars = []

        clc_class_names_level_1 = [
            " ".join(
                CorineLandCoverClassLevel1(int(str(c)[0])).name.split("_")
            ).capitalize()
            for c in set(self.clc_classes_corine)
        ]
        clc_class_names_level_2 = [
            corine_classes[CorineLandCoverClass(c)]
            for c in set(self.clc_classes_corine)
        ]
        x_list = [str(i) for i in list(set(self.clc_classes_corine))]
        y_list = [v * 100 for v in self.f1_scores]
        for name_level_1, name_level_2, x, y in zip(
            clc_class_names_level_1, clc_class_names_level_2, x_list, y_list
        ):
            bars.append(
                pgo.Bar(
                    name=name_level_2,
                    x=[x],
                    y=[y],
                    legendgroup=name_level_1,
                    legendgrouptitle_text=name_level_1,
                )
            )
        fig = pgo.Figure(
            data=bars,
            layout=pgo.Layout(
                {
                    "yaxis_range": [0, 100],
                    "xaxis_dtick": 1,
                    "autotypenumbers": "strict",
                    "legend": {
                        "yanchor": "top",
                        "x": 0,
                        "y": -0.1,
                        "orientation": "h",
                    },
                },
                showlegend=True,
            ),
            # updatemenus=[
            #     {
            #         "type": "buttons",
            #         "buttons": [
            #             {
            #                 "label": "≡",
            #                 "method": "relayout",
            #                 "args": ["showlegend", False],
            #                 "args2": ["showlegend", True],
            #             }
            #         ],
            #     }
            # ],
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def _create_figure_single_class(self):
        class_labels = ["Other classes", CorineClass(self.corine_class).name]
        fig = pgo.Figure(
            data=pgo.Heatmap(
                z=self.confusion_matrix,
                x=class_labels,
                y=class_labels,
                text=self.confusion_matrix,
                texttemplate="%{text:.2f}",
            ),
            # layout=pgo.Layout(title={"subtitle": {"text": ", ".join(class_labels)}}),
        )
        fig.update_yaxes(title_text="Corine Land Cover Class in OSM")
        fig.update_xaxes(title_text="Corine Land Cover Class (actual)")
        # TODO add legend with corine land cover classes mapped to meaningful titles?

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
