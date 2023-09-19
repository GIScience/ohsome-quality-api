import logging

import dateutil
import plotly.graph_objects as pgo
from geojson import Feature
from numpy import mean

from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic


class BuildingComparison(BaseIndicator):
    def __init__(
        self,
        topic: BaseTopic,
        feature: Feature,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )
        self.area_osm: float | None = None
        self.area_references: dict | None = None

        # TODO: Evaluate thresholds
        self.th_high = 0.8  # Above or equal to this value label should be green
        self.th_low = 0.2  # Above or equal to this value label should be yellow

    async def preprocess(self) -> None:
        # first get area of reference data because if no reference data exists we can
        # stop here
        # TODO
        self.area_references = {"EUBUCCO": 2.0676, "Microsoft Buildings": 6.555}
        query_result = await ohsome_client.query(
            self.topic,
            self.feature,
        )
        self.area_osm = query_result["result"][0]["value"] / (1000 * 1000)
        self.result.timestamp_osm = dateutil.parser.isoparse(
            query_result["result"][0]["timestamp"]
        )

    def calculate(self) -> None:
        # TODO: put checks into check_corner_cases. Let result be undefined.
        assert self.area_osm is not None
        assert self.area_references is not None
        for v in self.area_references.values():
            assert v != 0

        self.result.value = float(
            mean([self.area_osm / v for v in self.area_references.values()])
        )

        if self.result.value >= self.th_high:
            self.result.class_ = 5
        elif self.result.value >= self.th_low:
            self.result.class_ = 3
        else:
            self.result.class_ = 1

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        fig = pgo.Figure()
        fig.add_trace(
            pgo.Bar(
                name="Reference Data",
                x=["OSM"] + list(self.area_references.keys()),
                y=[self.area_osm] + list(self.area_references.values()),
            )
        )

        fig.update_layout(title_text=("Building Comparison"))
        fig.update_yaxes(title_text="Building Area [km²]")

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
