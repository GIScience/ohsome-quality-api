import logging
from string import Template

import plotly.graph_objects as pgo
from dateutil import parser
from geojson import Feature

from ohsome_quality_api.indicators.base import BaseIndicator
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

        template = Template(self.templates.result_description)
        result_description = template.safe_substitute(
            {
                "value": round(self.result.value * 100, 2),
            }
        )
        self.result.description = (
            self.templates.label_description[self.result.label]
            + " "
            + result_description
        )

        if self.result.label != "undefined":
            self.result.description += (
                " Note that the area of overlapping OSM land cover polygons "
                + "will be counted multiple times."
            )

    def create_figure(self) -> None:
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
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

        fig.add_layout_image(
            dict(
                source="https://raw.githubusercontent.com/GIScience/ohsome-quality-api/refs/heads/figure_background_logo/ohsome_quality_api/indicators/heigit_logo.png",
                xref="paper",
                yref="paper",
                x=0.9,
                y=-0.03,
                sizex=0.2,
                sizey=0.2,
                sizing="contain",
                opacity=0.3,
                layer="below",
            )
        )
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
