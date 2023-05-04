from io import StringIO
from math import pi
from string import Template

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from geojson import Feature

from ohsome_quality_analyst.attributes.models import Attribute
from ohsome_quality_analyst.indicators.base import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.topics.models import BaseTopic as Topic


class AttributeCompleteness(BaseIndicator):
    """
    Attribute completeness of map features.

    The ratio of features of a given topic to features of the same topic with additional
    (expected) attributes.

    Terminology:
        topic: Category of map features. Translates to a ohsome filter.
        attribute: Additional (expected) tag(s) describing a map feature. Translates to
            a ohsome filter.

    Example: How many buildings (topic) have height information (attribute)?

    Premise: Every map feature of a given topic should have certain additional
        attributes.
    """

    # TODO make attribute a list
    def __init__(self, topic: Topic, feature: Feature, attribute: Attribute) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.attribute = attribute
        self.ratio = None
        self.absolute_value_1 = None
        self.absolute_value_2 = None

    async def preprocess(self) -> None:
        # Get attribute filter
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            attribute=self.attribute,
        )
        timestamp = response["ratioResult"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        self.ratio = self.result.value = response["ratioResult"][0]["ratio"]
        self.absolute_value_1 = response["ratioResult"][0]["value"]
        self.absolute_value_2 = response["ratioResult"][0]["value2"]

    def calculate(self) -> None:
        # self.ratio can be of type float, NaN if no features of filter1
        # are in the region or None if the topic has no filter2
        if self.ratio == "NaN" or self.ratio is None:
            self.ratio = None
            self.result.value = None
            return
        description = Template(self.metadata.result_description).substitute(
            result=round(self.ratio, 1),
            all=round(self.absolute_value_1, 1),
            matched=round(self.absolute_value_2, 1),
        )
        if self.absolute_value_1 == 0:
            self.result.description = description + "No features in this region"
            return

        if self.ratio >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        elif self.threshold_yellow > self.ratio >= self.threshold_red:
            self.result.class_ = 3
            self.result.description = (
                description + self.metadata.label_description["yellow"]
            )
        else:
            self.result.class_ = 1
            self.result.description = (
                description + self.metadata.label_description["red"]
            )

    def create_figure(self) -> None:
        """Create a gauge chart.

        The gauge chart shows the percentage of features having the requested
        attribute(s).
        """

        def rotate(ratio, offset=(0, 0)):
            theta = ratio * pi
            c, s = np.cos(theta), np.sin(theta)
            r = np.array(((c, -s), (s, c)))
            return np.matmul(r.T, (-1, 0)) + offset

        fig = go.Figure(
            go.Indicator(
                domain={"x": [0, 1], "y": [0, 1]},
                mode="gauge",
                title={"text": "Attribute completeness", "font": {"size": 40}},
                type="indicator",
                gauge={
                    "axis": {
                        "range": [None, 100],
                        "tickwidth": 1,
                        "tickcolor": "darkblue",
                        "ticksuffix": "%",
                        "tickfont": dict(color="black", size=20),
                    },
                    "bar": {"color": "rgba(0,0,0,0)"},
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
            xaxis={"showgrid": False, "range": [-1, 1]},
            yaxis={"showgrid": False, "range": [0, 1]},
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=False,
        )

        fig.update_xaxes(visible=False)

        fig.update_yaxes(visible=False)

        base = [0, 0]
        # todo: test if we can remove the base stuff
        fig.add_annotation(
            ax=base[0],
            ay=base[1],
            axref="x",
            ayref="y",
            x=rotate(ratio=self.ratio)[0],
            y=rotate(ratio=self.ratio)[1],
            xref="x",
            yref="y",
            showarrow=True,
            arrowhead=0,
            arrowsize=1,
            arrowwidth=4,
        )

        fig.add_annotation(
            text=f"{self.ratio * 100:.1f}%",
            align="center",
            font=dict(color="black", size=35),
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.2,
            borderwidth=0,
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

        img_data = StringIO()
        plt.tight_layout()
        plt.savefig(img_data, format="svg")
        self.result.svg = img_data.getvalue()
        plt.close("all")
