import logging
from datetime import datetime
from string import Template

import plotly.graph_objects as go
from babel.numbers import format_decimal, format_percent
from dateutil.parser import isoparse
from fastapi_i18n import _, get_locale
from geojson import Feature

from ohsome_quality_api.attributes.definitions import (
    build_attribute_filter,
    build_attribute_title,
)
from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome_api import client as ohsome_api_client
from ohsome_quality_api.topics.models import Topic

logger = logging.getLogger(__name__)


def is_ohsomedb_enabled() -> bool:
    ohsomedb_enabled = get_config_value("ohsomedb_enabled")
    if ohsomedb_enabled or ohsomedb_enabled in ("True", "true"):  # noqa: SIM103
        return True
    else:
        return False


class AttributeCompleteness(BaseIndicator):
    """
    Attribute completeness of map features.

    The ratio of features of a given topic to features of the same topic with additional
    (expected) attributes.

    Terminology:
        topic: Category of map features. Translates to a ohsome filter.
        attribute: Additional (expected) tag(s) describing a map feature.
            attribute_keys: a set of predefined attributes wich will be
                translated to an ohsome filter
            attribute_filter: ohsome filter query representing custom attributes
            attribute_title:  Title describing the attributes represented by
                the Attribute Filter

    Example: How many buildings (topic) have height information (attribute)?

    Premise: Every map feature of a given topic should have certain additional
        attributes.

    Limitation: Limited to one attribute.
    """

    # TODO make attribute a list
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
        attribute_keys: list[str] | None = None,
        attribute_filter: str | None = None,
        attribute_title: str | None = None,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow: float = 0.75
        self.threshold_red: float = 0.25
        self.absolute_value_1: float = 0
        self.absolute_value_2: float = 0

        self.attribute_keys = attribute_keys
        self.attribute_filter = build_attribute_filter(
            attribute_filter, attribute_keys, topic.key
        )
        self.attribute_title = build_attribute_title(
            attribute_title, attribute_keys, topic.key
        )

    async def preprocess(self):
        raw = await ohsome_api_client.metadata()
        latest_timestamp = datetime.fromisoformat(
            raw["temporalExtent"]["latestTimestamp"]
        )
        end = latest_timestamp.strftime("%Y-%m-01")
        start = "2008-" + latest_timestamp.strftime("%m-%d")

        result_1 = await ohsome_api_client.features(
            aoi=self.feature.geometry,
            measure=self.topic.aggregation_type,
            ohsome_filter=self.topic.filter,
            time_series={"start": start, "end": end},
        )
        result_2 = await ohsome_api_client.features(
            aoi=self.feature.geometry,
            measure=self.topic.aggregation_type,
            ohsome_filter=self.attribute_filter,
            time_series={"start": start, "end": end},
        )

        absolute_value_1 = result_1[-1]["value"]
        absolute_value_2 = result_2[-1]["value"]

        match self.topic.aggregation_type:
            case "count":
                self.absolute_value_1 = absolute_value_1
                self.absolute_value_2 = absolute_value_2
            case "length":
                self.absolute_value_1 = absolute_value_1 * 0.001  # in km
                self.absolute_value_2 = absolute_value_2 * 0.001  # in km
            case "area":
                self.absolute_value_1 = absolute_value_1 * 0.001 * 0.001  # in square km
                self.absolute_value_2 = absolute_value_2 * 0.001 * 0.001  # in square km
            case _:
                raise ValueError("Unexpected aggregation type.")

        self.result.timestamp_osm = isoparse(result_1[-1]["timestamp"])

    def calculate(self) -> None:
        if (
            self.absolute_value_1 == 0
            or self.absolute_value_1 is None
            or self.absolute_value_2 is None
        ):
            self.result.description += _(" No features in this region")
            return

        self.result.value = self.absolute_value_2 / self.absolute_value_1
        description = self.create_description()

        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                description + self.templates.label_description.green
            )
        elif self.threshold_yellow > self.result.value >= self.threshold_red:
            self.result.class_ = 3
            self.result.description = (
                description + self.templates.label_description.yellow
            )
        else:
            self.result.class_ = 1
            self.result.description = description + self.templates.label_description.red

    def create_description(self):
        if self.result.value is None:
            raise TypeError("Result value should not be None.")
        else:
            result = format_percent(self.result.value, format="0%", locale=get_locale())
        if self.attribute_title is None:
            raise TypeError("Attribute title should not be None.")
        else:
            tags = str(
                _("attributes ") + self.attribute_title
                if self.attribute_keys and len(self.attribute_keys) > 1
                else _("attribute ") + self.attribute_title
            )
        all_, matched = self.compute_units_for_all_and_matched()
        return Template(self.templates.result_description).substitute(
            result=result,
            all=all_,
            matched=matched,
            topic=self.topic.name,
            tags=tags,
        )

    def create_figure(self) -> None:
        """Create a gauge chart.

        The gauge chart shows the percentage of features having the requested
        attribute(s).
        """
        if self.result.label == "undefined":
            logger.info("Result is undefined. Skipping figure creation.")
            return

        fig = go.Figure(
            go.Indicator(
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

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def compute_units_for_all_and_matched(self) -> tuple[str, str]:
        assert self.absolute_value_1 is not None  # noqa
        assert self.absolute_value_2 is not None  # noqa
        if self.topic.aggregation_type == "count":
            all_ = _("{absolute_value} elements").format(
                absolute_value=int(self.absolute_value_1)
            )
            matched = f"{int(self.absolute_value_2)} {_('elements')}"
        elif self.topic.aggregation_type == "area":
            all_ = f"{format_decimal(self.absolute_value_1, locale=get_locale())} km²"
            matched = (
                f"{format_decimal(self.absolute_value_2, locale=get_locale())} km²"
            )
        elif self.topic.aggregation_type == "length":
            all_ = f"{format_decimal(self.absolute_value_1, locale=get_locale())} km"
            matched = f"{format_decimal(self.absolute_value_2, locale=get_locale())} km"
        else:
            raise ValueError("Invalid aggregation_type")
        return all_, matched
