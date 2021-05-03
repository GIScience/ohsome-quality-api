"""
TODO:
    Describe this module and how to implement child classes
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from typing import Dict, Literal, Optional

import matplotlib.pyplot as plt
from dacite import from_dict
from geojson import FeatureCollection

from ohsome_quality_analyst.utils.definitions import get_layer_definition, get_metadata


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
    hex_endpoint: Optional[str] = None
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
    data: Optional[dict] = None


class BaseIndicator(metaclass=ABCMeta):
    """The base class of every indicator."""

    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
        data: dict = None,
    ) -> None:

        self.bpolys: str = bpolys
        self.data: Optional[dict] = data

        # setattr(object, key, value) could be used instead of relying on from_dict.
        metadata = get_metadata("indicators", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)

        layer = get_layer_definition(layer_name)
        self.layer: LayerDefinition = from_dict(data_class=LayerDefinition, data=layer)
        self.result: Result = Result(
            timestamp_oqt=datetime.utcnow(),
            timestamp_osm=None,
            label="undefined",
            value=None,
            description=self.metadata.label_description["undefined"],
            svg=self._get_default_figure(),
        )

    @abstractmethod
    async def preprocess(self) -> bool:
        """Get fetch and prepocess data

        Fetch data from the ohsome API and/or from the geodatabase asynchronously.
        Preprocess data for calculation and save those as attributes.
        Returns True if preprocessing was successful otherwise False.
        """
        pass

    @abstractmethod
    def calculate(self) -> bool:
        """ "Calculate indicator results

        Writes results to the result attribute.
        Returns True if calculation was successful otherwise False.
        """
        pass

    @abstractmethod
    def create_figure(self) -> bool:
        """ "Create figure plotting indicator results

        Writes an SVG figure to the svg attribute of the result attribute.
        Returns True if figure creation was successful otherwise False.
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
