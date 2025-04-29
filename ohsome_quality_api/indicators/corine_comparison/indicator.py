from pathlib import Path

from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator


class CorineComparison(BaseIndicator):
    pass

    async def preprocess(self) -> None:
        with open(Path(__file__).parent / "query.sql", "r") as file:
            query = file.read()
        results = await client.fetch(query, str(self.feature["geometry"]))
        self.clc_classes_corine = [r[0] for r in results]
        self.clc_classes_osm = [r[1] for r in results]
        self.areas = [r[2] for r in results]

    def calculate(self) -> None:
        pass

    def create_figure(self) -> None:
        pass
