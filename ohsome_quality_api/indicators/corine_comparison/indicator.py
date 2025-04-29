from pathlib import Path
import logging

import matplotlib.pyplot as plt
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator

from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    classification_report,
)


class CorineComparison(BaseIndicator):
    """
    Only shows class for which OSM has data.

    Ergänzend zu dem Corine Completeness Indicator
    """

    async def preprocess(self) -> None:
        with open(Path(__file__).parent / "query.sql", "r") as file:
            query = file.read()
        results = await client.fetch(query, str(self.feature["geometry"]))
        self.clc_classes_corine = [r[0] for r in results]
        self.clc_classes_osm = [r[1] for r in results]
        self.areas = [r[2] / 1_000_000 for r in results]  # sqkm

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

        report = classification_report(
            self.clc_classes_corine,
            self.clc_classes_osm,
            sample_weight=self.areas,
        )
        logging.info(report)

    def create_figure(self) -> None:
        # TODO: remove matplotlib dep
        ConfusionMatrixDisplay(self.confusion_matrix).plot()
        plt.show()
        pass
