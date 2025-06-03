from dateutil import parser
from geojson import Feature
from indicators.base import BaseIndicator

from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic as Topic


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
        self.result.description = (
            self.templates.label_description["green"]
            + self.templates.result_description
        )

    def create_figure(self) -> None:
        pass
