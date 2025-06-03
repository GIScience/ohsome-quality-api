import plotly.graph_objects as pgo
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

        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow

    async def preprocess(self):
        # get osm building area

        result = await ohsome_client.query(self.topic, self.feature)
        self.osm_area_ratio = result["result"][0]["value"] or 0.0  # if None
        timestamp = result["result"][0]["timestamp"]
        self.result.timestamp_osm = parser.isoparse(timestamp)

    def calculate(self):
        self.osm_area_ratio /= 1000000
        self.result.value = round(self.osm_area_ratio, 2)
        if self.result.value >= self.th_high:
            self.result.class_ = 5
        elif self.th_high > self.result.value >= self.th_low:
            self.result.class_ = 3
        elif self.th_low > self.result.value >= 0:
            self.result.class_ = 1
        self.result.description = (
            self.templates.label_description[self.result.label]
            + self.templates.result_description
        )

    def create_figure(self) -> None:
        fig = pgo.Figure()
        fig.add_trace(pgo.Bar(x=["name"], y=[self.osm_area_ratio * 100]))
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
