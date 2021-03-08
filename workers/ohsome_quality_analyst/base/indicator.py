"""
TODO:
    Describe this module and how to implement child classes
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, Literal

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
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)
        layer = get_layer_definition(layer_name)
        self.layer: LayerDefinition = from_dict(data_class=LayerDefinition, data=layer)
        self.result: Result = Result(None, None, None, None)

    @abstractmethod
    def preprocess(self) -> None:
        pass

    @abstractmethod
    def calculate(self) -> None:
        pass

    @abstractmethod
    def create_figure(self) -> None:
        pass
