import logging
from datetime import datetime
from string import Template

import plotly.graph_objects as pgo
from babel.numbers import format_percent
from dateutil.parser import isoparse
from fastapi_i18n import _, get_locale
from geojson import Feature

from ohsome_quality_api.geodatabase import client as geodatabase_client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome_api import client as ohsome_api_client
from ohsome_quality_api.topics.models import Topic

logger = logging.getLogger(__name__)


class LandCoverCompleteness(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)

        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow
        self.area_osm: float = 0
        self.area_feature: float = 0

    async def preprocess(self):
        self.area_feature = await geodatabase_client.area(self.feature)

        raw = await ohsome_api_client.metadata()
        latest_timestamp = datetime.fromisoformat(
            raw["temporalExtent"]["latestTimestamp"]
        )
        end = latest_timestamp.strftime("%Y-%m-01")
        start = "2008-" + latest_timestamp.strftime("%m-%d")

        result = await ohsome_api_client.features(
            aoi=self.feature.geometry,
            measure=self.topic.aggregation_type,
            ohsome_filter=self.topic.filter,
            time_series={"start": start, "end": end},
        )

        if result["value"][-1]:
            self.area_osm = result["value"][-1] / 1_000_000
        else:
            self.area_osm = 0
        self.result.timestamp_osm = isoparse(result["timestamp"][-1])

    def calculate(self):
        area_ratio = self.area_osm / self.area_feature

        self.result.value = round(area_ratio, 2)
        if self.result.value >= self.th_high:
            self.result.class_ = 5
        elif self.th_high > self.result.value >= self.th_low:
            self.result.class_ = 3
        elif self.th_low > self.result.value >= 0:
            self.result.class_ = 1

        template = Template(self.templates.result_description)
        result_description = template.safe_substitute(
            {
                "value": format_percent(
                    self.result.value, format="##0.##%", locale=get_locale()
                ),
            }
        )
        self.result.description = (
            getattr(self.templates.label_description, self.result.label)
            + " "
            + result_description
        )

        if self.result.label != "undefined":
            self.result.description += _(
                " Note that the area of overlapping OSM land cover polygons "
                + "will be counted multiple times."
            )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logger.info("Result is undefined. Skipping figure creation.")
            return

        fig = pgo.Figure(
            pgo.Indicator(
                domain={"x": [0, 1], "y": [0, 1]},
                mode="gauge+number",
                value=self.result.value * 100,
                number={"suffix": "%"},
                type="indicator",
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickwidth": 1,
                        "tickcolor": "darkblue",
                        "ticksuffix": "%",
                        "tickfont": dict(color="black", size=20),
                    },
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, self.th_low * 100], "color": "tomato"},
                        {
                            "range": [
                                self.th_low * 100,
                                self.th_high * 100,
                            ],
                            "color": "gold",
                        },
                        {
                            "range": [self.th_high * 100, 100],
                            "color": "darkseagreen",
                        },
                    ],
                },
            )
        )

        fig.update_layout(
            font={"color": "black", "family": "Arial"},
            xaxis={"showgrid": False, "range": [-1, 1], "fixedrange": True},
            yaxis={"showgrid": False, "range": [0, 1], "fixedrange": True},
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=True,
        )

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
