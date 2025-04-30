from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    f1_score,
)

from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator


class LandCoverThematicAccuracy(BaseIndicator):
    """
    Only shows class for which OSM has data.

    Ergänzend zu dem Corine Completeness Indicator
    """

    async def preprocess(self) -> None:
        with open(Path(__file__).parent / "query.sql", "r") as file:
            query = file.read()
        results = await client.fetch(query, str(self.feature["geometry"]))
        self.clc_classes_corine = [r["clc_class_corine"] for r in results]
        self.clc_classes_osm = [r["clc_class_osm"] for r in results]
        self.areas = [r["area"] / 1_000_000 for r in results]  # sqkm

    def calculate(self) -> None:
        self.confusion_matrix = confusion_matrix(
            self.clc_classes_corine,
            self.clc_classes_osm,
            sample_weight=self.areas,
            normalize="all",
        )

        self.f1_score = f1_score(
            self.clc_classes_corine,
            self.clc_classes_osm,
            average="weighted",
            sample_weight=self.areas,
        )
        self.result.value = self.f1_score

        if self.f1_score > 0.8:
            self.result.class_ = 5
        elif self.f1_score > 0.5:
            self.result.class_ = 3
        else:
            self.result.class_ = 1

        self.result.description = self.templates.label_description[self.result.label]

        self.report = classification_report(
            self.clc_classes_corine,
            self.clc_classes_osm,
            sample_weight=self.areas,
        )

    def create_figure(self) -> None:
        # TODO: remove matplotlib dep
        ConfusionMatrixDisplay(self.confusion_matrix).plot()
        plt.show()
        pass
