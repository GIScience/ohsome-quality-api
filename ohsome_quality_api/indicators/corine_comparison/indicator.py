from pathlib import Path
import json

from ohsome_quality_api.indicators.base import BaseIndicator


class CorineComparison(BaseIndicator):
    pass

    def preprocess(self) -> None:
        with open(Path(__file__).parent / "query.sql", "r") as file:
            query = file.read().format(geojson=json.dumps(self.feature["geometry"]))
        self.areas = []
        self.clc_classes_corine = []
        self.clc_classes_osm = []

    def calculate(self) -> None:
        pass

    def create_figure(self) -> None:
        pass
