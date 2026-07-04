"""An Indicator for testing purposes."""

from datetime import datetime
from string import Template

from geojson import Feature

from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import Topic


class Minimal(BaseIndicator):
    def __init__(self, topic: Topic, feature: Feature) -> None:
        super().__init__(topic=topic, feature=feature)
        self.count = 0

    async def preprocess(self) -> None:
        self.count = 1
        self.result.timestamp_osm = datetime.now()

    def calculate(self) -> None:
        description = Template(self.templates.result_description).substitute()
        self.result.value = 1.0
        self.result.description = description + self.templates.label_description.green

    def create_figure(self) -> None:
        # Do nothing ...
        return None
