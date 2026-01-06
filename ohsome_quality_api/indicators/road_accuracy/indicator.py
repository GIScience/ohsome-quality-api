import logging

from geojson import Feature

from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import Topic

logger = logging.getLogger(__name__)


class RoadAccuracy(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )

    def preprocess(self) -> None:
        pass

    def calculate(self) -> None:
        pass

    def create_figure(self) -> None:
        pass
