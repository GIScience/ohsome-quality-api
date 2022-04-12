"""
TODO:
    Describe this module and how to implement child classes
"""

import json
import os
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from typing import Dict, Literal, Optional

import matplotlib.pyplot as plt
from dacite import from_dict
from geojson import Feature
from jinja2 import Environment, FileSystemLoader

from ohsome_quality_analyst.utils.definitions import (
    get_attribution,
    get_layer_definition,
    get_metadata,
)
from ohsome_quality_analyst.utils.helper import flatten_dict, json_serialize


@dataclass
class Metadata:
    """Metadata of an indicator as defined in the metadata.yaml file"""

    name: str
    description: str
    label_description: Dict
    result_description: str


@dataclass
class LayerDefinition:
    """Definitions of a layer as defined in the layer_definition.yaml file.

    The definition consist of the ohsome API Parameter needed to create the layer.
    """

    name: str
    description: str
    endpoint: str
    filter: str
    ratio_filter: Optional[str] = None
    source: Optional[str] = None


@dataclass
class Result:
    """The result of the Indicator.

    Attributes:
        timestamp_oqt (datetime): Timestamp of the creation of the indicator
        timestamp_osm (datetime): Timestamp of the used OSM data
            (e.g. Latest timestamp of the ohsome API results)
        label (str): Traffic lights like quality label
        value (float): The result value as float ([0, 1])
        description (str): Description of the result
        svg (str): Figure of the result as SVG
    """

    timestamp_oqt: datetime
    timestamp_osm: Optional[datetime]
    label: Literal["green", "yellow", "red", "undefined"]
    value: Optional[float]
    description: str
    svg: str
    html: str


class BaseIndicator(metaclass=ABCMeta):
    """The base class of every indicator."""

    def __init__(
        self,
        layer_name: str,
        feature: Feature,
    ) -> None:
        self.feature = feature

        # setattr(object, key, value) could be used instead of relying on from_dict.
        metadata = get_metadata("indicators", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)

        self.layer: LayerDefinition = from_dict(
            data_class=LayerDefinition, data=get_layer_definition(layer_name)
        )
        self.result: Result = Result(
            # UTC datetime object representing the current time.
            timestamp_oqt=datetime.now(timezone.utc),
            timestamp_osm=None,
            label="undefined",
            value=None,
            description=self.metadata.label_description["undefined"],
            svg=self._get_default_figure(),
            html="",
        )

    def as_feature(self, flatten: bool = False) -> Feature:
        """Returns a GeoJSON Feature object.

        The properties of the Feature contains the attributes of the indicator.
        The geometry (and properties) of the input GeoJSON object is preserved.

        Args:
            flatten (bool): If true flatten the properties.
        """
        properties = {
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.name,
            },
            "layer": {
                "name": self.layer.name,
                "description": self.layer.description,
            },
            "result": vars(self.result).copy(),
            "data": self.data,
            **self.feature.properties,
        }
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
        """All Indicator object attributes except feature, result, metadata and layer.

        Note:
            Attributes will be dumped and immediately loaded again by the `json`
            library. In this process a custom function for serializing data types which
            are not supported by the `json` library (E.g. numpy datatypes or objects of
            the `BaseModelStats` class) will be executed.
        """
        data = vars(self).copy()
        data.pop("result")
        data.pop("metadata")
        data.pop("layer")
        data.pop("feature")
        return json.loads(json.dumps(data, default=json_serialize).encode())

    @classmethod
    def attribution(cls) -> str:
        """Data attribution as text.

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
        """Return a SVG as default figure for indicators"""
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
        template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
        )
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("indicator_template.html")

        def traffic_light(label, red="#bbb", yellow="#bbb", green="#bbb"):
            dot_css = (
                "style='height: 25px; width: 25px; background-color: {0};"
                "border-radius: 50%; display: inline-block;'"
            )
            return (
                "<span {0} class='dot'></span>\n<span {1} class='dot'>"
                "</span>\n<span {2} class='dot'></span>\n {3}".format(
                    dot_css.format(red),
                    dot_css.format(yellow),
                    dot_css.format(green),
                    label,
                )
            )

        if self.result.label == "red":
            traffic_light = traffic_light("Bad Quality", red="#FF0000")
        elif self.result.label == "yellow":
            traffic_light = traffic_light("Medium Quality", yellow="#FFFF00")
        elif self.result.label == "green":
            traffic_light = traffic_light("Good Quality", green="#008000")
        else:
            traffic_light = traffic_light("Undefined Quality")
        self.result.html = template.render(
            indicator_name=self.metadata.name,
            layer_name=self.layer.name,
            svg=self.result.svg,
            result_description=self.result.description,
            indicator_description=self.metadata.description,
            traffic_light=traffic_light,
        )
