"""
TODO:
    Describe this module and how to implement child classes
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, Literal, Optional

from dacite import from_dict
from geojson import FeatureCollection

import ohsome_quality_analyst.geodatabase.client as db_client
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
    ratio_filter: Optional[str] = None


@dataclass
class Result:
    """The result of the Indicator."""

    label: Literal["green", "yellow", "red", "undefined"]
    value: float
    description: str
    svg: str


class BaseIndicator(metaclass=ABCMeta):
    """
    The base class of every indicator.

    An indicator can be created in two ways:

    One; Calculate from scratch for an area of interest.
    This is done by providing a bounding polygone as input parameter.

    Two; Fetch the precaclulated results from the Geodatabase.
    This is done by providing the dataset name and feature id as input parameter.
    """

    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        self.dataset = dataset
        self.feature_id = feature_id
        if bpolys is not None:
            self.bpolys = bpolys
        elif dataset is not None and feature_id is not None:
            self.bpolys = db_client.get_bpolys_from_db(self.dataset, self.feature_id)
        else:
            raise ValueError(
                "Provide either a bounding polygon "
                + "or dataset name and feature id as parameter."
            )

        # setattr(object, key, value) could be used instead of relying on from_dict.
        metadata = get_metadata("indicators", type(self).__name__)
        self.metadata = from_dict(data_class=Metadata, data=metadata)
        layer = get_layer_definition(layer_name)
        self.layer = from_dict(data_class=LayerDefinition, data=layer)
        self.result = Result(
            label="undefined",
            value=None,
            description=self.metadata.label_description["undefined"],
            svg=None,
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

        Writes an SVG figure to the SVG attribute of the result attribute.
        Returns True if figure creation was successful otherwise False.
        """
        pass
