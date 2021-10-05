"""
TODO:
    Describe this module and how to implement child classes
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from typing import Dict, Literal, Optional

import matplotlib.pyplot as plt
from dacite import from_dict
from geojson import Feature

from ohsome_quality_analyst.utils.definitions import (
    INDICATOR_LAYER,
    get_layer_definition,
    get_metadata,
)


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


@dataclass
class Result:
    """The result of the Indicator."""

    timestamp_oqt: datetime
    timestamp_osm: Optional[datetime]
    label: Literal["green", "yellow", "red", "undefined"]
    value: Optional[float]
    description: str
    svg: str


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
        )

        self._validate_indicator_layer(self.__class__.__name__, layer_name)

    def as_feature(self) -> Feature:
        """Returns a GeoJSON Feature object.

        The properties of the Feature contains the attributes of the indicator.
        The geometry (and properties) of the input GeoJSON object is preserved.
        """
        result = vars(self.result).copy()
        # Prefix all keys of the dictionary
        properties = {
            "metadata.name": self.metadata.name,
            "metadata.description": self.metadata.description,
            "layer.name": self.layer.name,
            "layer.description": self.layer.description,
            **{"result." + str(key): val for key, val in result.items()},
            **{"data." + str(key): val for key, val in self.data.items()},
            **self.feature.properties,
        }
        return Feature(geometry=self.feature.geometry, properties=properties)

    @property
    def data(self) -> dict:
        """All indicator attributes except feature, result, metadata and layer."""
        data = vars(self).copy()
        data.pop("result")
        data.pop("metadata")
        data.pop("layer")
        data.pop("feature")
        return data

    @abstractmethod
    async def preprocess(self) -> None:
        """Get fetch and prepocess data.

        Fetch data from the ohsome API and/or from the geodatabase asynchronously.
        Preprocess data for calculation and save those as attributes.
        """
        pass

    @abstractmethod
    def calculate(self) -> None:
        """Calculate indicator results.

        Writes results to the result attribute.
        """
        pass

    @abstractmethod
    def create_figure(self) -> None:
        """Create figure plotting indicator results.

        Writes an SVG figure to the svg attribute of the result attribute.
        """
        pass

    def _validate_indicator_layer(self, indicator_name, layer_name):
        indicator_layer = (indicator_name, layer_name)
        if indicator_layer not in INDICATOR_LAYER:
            raise ValueError(
                "Indicator layer combination is invalid: " + str(indicator_layer)
            )

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
