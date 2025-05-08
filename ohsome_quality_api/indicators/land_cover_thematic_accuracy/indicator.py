import logging
from datetime import datetime, timezone
from pathlib import Path

import plotly.graph_objects as pgo
from geojson import Feature
from sklearn.metrics import classification_report, confusion_matrix, f1_score

from ohsome_quality_api.api.request_models import CorineClass
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic as Topic


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

        self.result.description = self.templates.label_description[self.result.label]
        self.result.description = self.templates.result_description

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
            parts = CorineClass(c).name.split("_")
            title = " ".join(parts).lower().title()
            class_labels.append(title)
        fig = pgo.Figure(
            data=[
                pgo.Bar(
                    name="OSM building area",
                    x=list(set(class_labels)),
                    # x=self.f1_scores,
                    y=[v * 100 for v in self.f1_scores],
                )
            ],
            layout=pgo.Layout({"yaxis_range": [0, 100]}),
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def _create_figure_single_class(self):
        class_labels = []
        for c in self.clc_classes_corine:
            parts = CorineClass(c).name.split("_")
            title = " ".join(parts).lower().title()
            class_labels.append(title)
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
        fig.update_yaxes(title_text="Corine Land Cover Class")
        fig.update_xaxes(title_text="Corine Land Cover Class")
        # TODO add legend with corine land cover classes mapped to meaningful titles?

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
