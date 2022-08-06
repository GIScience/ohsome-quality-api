"""The base classes on which every indicator class is based on."""

import json
from abc import ABCMeta, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from io import StringIO
from typing import Dict, Literal, Optional

import matplotlib.pyplot as plt
from dacite import from_dict
from geojson import Feature

from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.definitions import get_attribution, get_metadata
from ohsome_quality_analyst.html_templates.template import (
    get_template,
    get_traffic_light,
)
from ohsome_quality_analyst.utils.helper import flatten_dict, json_serialize


@dataclass
class Metadata:
    """Metadata of an indicator as defined in the metadata.yaml file."""

    name: str
    description: str
    label_description: Dict
    result_description: str


@dataclass
class Result:
    """The result of the Indicator.

    Attributes:
        timestamp_oqt (datetime): Timestamp of the creation of the indicator
        timestamp_osm (datetime): Timestamp of the used OSM data
            (e.g. Latest timestamp of the ohsome API results)
        label (str): Traffic lights like quality label: `green`, `yellow` or `red`. The
            value is determined by the result classes
        value (float): The result value
        class_ (int): The result class. An integer between 1 and 5. It maps to the
            result labels. This value is used by the reports to determine an overall
            result.
        description (str): The result description.
        svg (str): Figure of the result as SVG
    """

    description: str
    svg: str
    html: str
    timestamp_oqt: datetime = datetime.now(timezone.utc)  # UTC datetime object
    timestamp_osm: Optional[datetime] = None
    value: Optional[float] = None
    class_: Optional[Literal[1, 2, 3, 4, 5]] = None

    @property
    def label(self) -> Literal["green", "yellow", "red", "undefined"]:
        labels = {1: "red", 2: "yellow", 3: "yellow", 4: "green", 5: "green"}
        return labels.get(self.class_, "undefined")


class BaseIndicator(metaclass=ABCMeta):
    """The base class of every indicator."""

    def __init__(
        self,
        layer: Layer,
        feature: Feature,
    ) -> None:
        self.layer: Layer = layer
        self.feature: Feature = feature
        # setattr(object, key, value) could be used instead of relying on from_dict.
        metadata = get_metadata("indicators", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)
        self.result: Result = Result(
            description=self.metadata.label_description["undefined"],
            svg=self._get_default_figure(),
            html="",
        )

    def as_feature(
        self,
        flatten: bool = False,
        include_data: bool = False,
        include_svg: bool = False,
        include_html: bool = False,
    ) -> Feature:
        """Return a GeoJSON Feature object.

        The properties of the Feature contains the attributes of the indicator.
        The geometry (and properties) of the input GeoJSON object is preserved.

        Args:
            flatten (bool): If true flatten the properties.
            include_data (bool): If true include additional data in the properties.
        """
        result = asdict(self.result)  # only attributes, no properties
        result["label"] = self.result.label  # label is a property
        result["class"] = result.pop("class_")
        properties = {
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
            },
            "layer": {
                "key": self.layer.key,
                "name": self.layer.name,
                "description": self.layer.description,
            },
            "result": result,
            **self.feature.properties,
        }
        if not include_svg:
            del properties["result"]["svg"]
        if not include_html:
            del properties["result"]["html"]
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
    def create_figure(self, include_svg: bool = True) -> None:
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

    def create_html(self, include_html: bool):
        if not include_html:
            self.result.html = None
            return
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
            layer_name=self.layer.name,
            svg=self.result.svg,
            result_description=self.result.description,
            indicator_description=self.metadata.description,
            traffic_light=traffic_light,
        )
