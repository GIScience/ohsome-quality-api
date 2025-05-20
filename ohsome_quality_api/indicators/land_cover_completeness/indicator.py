from pathlib import Path

from geodatabase import client
from indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from dateutil import parser
from ohsome_quality_api.topics.models import BaseTopic as Topic
from geojson import Feature

class LandCoverCompleteness(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)

    async def preprocess(self):
        # get osm building area

        result = await ohsome_client.query(self.topic, self.feature)
        self.osm_area = result["result"][0]["value"] or 0.0  # if None
        timestamp = result["result"][0]["timestamp"]
        self.result.timestamp_osm = parser.isoparse(timestamp)
    def calculate(self):
        pass
    def create_figure(self) -> None:
        pass


