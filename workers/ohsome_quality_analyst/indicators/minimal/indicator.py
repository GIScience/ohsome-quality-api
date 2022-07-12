"""An Indicator for testing purposes."""
from string import Template

import dateutil.parser
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.ohsome import client as ohsome_client


class Minimal(BaseIndicator):
    def __init__(self, layer: Layer, feature: Feature, thresholds: tuple) -> None:
        super().__init__(layer=layer, feature=feature, thresholds=thresholds)
        self.count = 0

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(self.layer, self.feature)
        self.count = query_results["result"][0]["value"]
        self.result.timestamp_osm = dateutil.parser.isoparse(
            query_results["result"][0]["timestamp"]
        )

    def calculate(self) -> None:
        description = Template(self.metadata.result_description).substitute()
        self.result.value = 1.0
        self.result.description = description + self.metadata.label_description["green"]

    def create_figure(self) -> None:
        pass
