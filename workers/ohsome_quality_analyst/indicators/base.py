"""The base classes on which every indicator class is based on."""

import json
from abc import ABCMeta, abstractmethod
from io import StringIO

import matplotlib.pyplot as plt
from geojson import Feature

from ohsome_quality_analyst.definitions import get_attribution, get_metadata
from ohsome_quality_analyst.html_templates.template import (
    get_template,
    get_traffic_light,
)
from ohsome_quality_analyst.indicators.models import Metadata, Result
from ohsome_quality_analyst.topics.models import BaseTopic as Topic
from ohsome_quality_analyst.utils.helper import flatten_dict, json_serialize


class BaseIndicator(metaclass=ABCMeta):
    """The base class of every indicator."""

    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        self.metadata: Metadata = get_metadata("indicators", type(self).__name__)
        self.topic: Topic = topic
        self.feature: Feature = feature
        self.result: Result = Result(
            description=self.metadata.label_description["undefined"],
            svg=self._get_default_figure(),
            html="",
        )

    def as_feature(self, flatten: bool = False, include_data: bool = False) -> Feature:
        """Return a GeoJSON Feature object.

        The properties of the Feature contains the attributes of the indicator.
        The geometry (and properties) of the input GeoJSON object is preserved.

        Args:
            flatten (bool): If true flatten the properties.
            include_data (bool): If true include additional data in the properties.
        """
        result = self.result.dict()  # only attributes, no properties
        result["label"] = self.result.label  # label is a property
        result["class"] = result.pop("class_")
        properties = {
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
            },
            "topic": {
                "key": self.topic.key,
                "name": self.topic.name,
                "description": self.topic.description,
            },
            "result": result,
            **self.feature.properties,
        }
        if include_data:
            properties["data"] = self.data
        if flatten:
            properties = flatten_dict(properties)
        if "id" in self.feature.keys():
            return Feature(
                id=self.feature.id,
                geometry=self.feature.geometry,
                properties=properties,
            )
        else:
            return Feature(
                geometry=self.feature.geometry,
                properties=properties,
            )

    @property
    def data(self) -> dict:
        """All Indicator object attributes except feature, result, metadata and topic.

        Note:
            Attributes will be dumped and immediately loaded again by the `json`
            library. In this process a custom function for serializing data types which
            are not supported by the `json` library (E.g. numpy datatypes or objects of
            the `BaseModelStats` class) will be executed.
        """
        data = vars(self).copy()
        data.pop("result")
        data.pop("metadata")
        data.pop("topic")
        data.pop("feature")
        return json.loads(json.dumps(data, default=json_serialize).encode())

    @classmethod
    def attribution(cls) -> str:
        """Return data attribution as text.

        Defaults to OpenStreetMap attribution.

        This property should be overwritten by the Sub Class if additional data
        attribution is necessary.
        """
        return get_attribution(["OSM"])

    @abstractmethod
    async def preprocess(self) -> None:
        """Get fetch and preprocess data.

        Fetch data from the ohsome API and/or from the geodatabase asynchronously.
        Preprocess data for calculation and save those as attributes.
        """
        pass

    @abstractmethod
    def calculate(self) -> None:
        """Calculate indicator results.

        Writes the results to the result attribute.
        """
        pass

    @abstractmethod
    def create_figure(self) -> None:
        """Create figure plotting indicator results.

        Writes an SVG figure to the svg attribute of the result attribute.
        """
        pass

    def _get_default_figure(self) -> str:
        """Return a SVG as default figure for indicators."""
        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        plt.figure(figsize=figsize)
        plt.text(
            5.5,
            0.5,
            "The creation of the Indicator was unsuccessful.",
            bbox={"facecolor": "white", "alpha": 1, "edgecolor": "none", "pad": 1},
            ha="center",
            va="center",
        )
        plt.axvline(5.5, color="w", linestyle="solid")
        plt.axis("off")

        svg_string = StringIO()
        plt.savefig(svg_string, format="svg")
        plt.close("all")
        return svg_string.getvalue()

    def create_html(self):
        if self.result.label == "red":
            traffic_light = get_traffic_light("Bad Quality", red="#FF0000")
        elif self.result.label == "yellow":
            traffic_light = get_traffic_light("Medium Quality", yellow="#FFFF00")
        elif self.result.label == "green":
            traffic_light = get_traffic_light("Good Quality", green="#008000")
        else:
            traffic_light = get_traffic_light("Undefined Quality")
        template = get_template("indicator")
        self.result.html = template.render(
            indicator_name=self.metadata.name,
            topic_name=self.topic.name,
            svg=self.result.svg,
            result_description=self.result.description,
            indicator_description=self.metadata.description,
            traffic_light=traffic_light,
        )
