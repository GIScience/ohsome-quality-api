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
        self.result.description = (
            self.templates.label_description[self.result.label]
            + self.templates.result_description
        )

    def create_figure(self) -> None:
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25

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
                        {"range": [0, self.threshold_red * 100], "color": "tomato"},
                        {
                            "range": [
                                self.threshold_red * 100,
                                self.threshold_yellow * 100,
                            ],
                            "color": "gold",
                        },
                        {
                            "range": [self.threshold_yellow * 100, 100],
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
                source="https://media.licdn.com/dms/image/v2/D560BAQE9rkvB7vB_cg/company-logo_200_200/company-logo_200_200/0/1711546373172/heigit_logo?e=2147483647&v=beta&t=pWdgVEOkz7VBhH2WbM5_DJeTs7RsdVXbolKU3ftS1iY",
                xref="paper",
                yref="paper",
                x=0.42,
                y=0.65,
                sizex=0.3,
                sizey=0.3,
                sizing="contain",
                opacity=0.3,
                layer="above",
            )
        )

        # fig.update_layout(template='plotly_white')

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw
        fig.show()
