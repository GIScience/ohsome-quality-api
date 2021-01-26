"""
TODO:
    Describe this module and how to implement child classes
"""

import os
import uuid
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple

from dacite import from_dict
from geojson import FeatureCollection

from ohsome_quality_tool.geodatabase.client import (
    get_bpolys_from_db,
    get_indicator_results_from_db,
    save_indicator_results_to_db,
)
from ohsome_quality_tool.utils.definitions import (
    DATA_PATH,
    get_indicator_metadata,
    get_layer_definition,
    logger,
)


@dataclass
class Metadata:
    """Metadata of an indicator as defined in the metadata.yaml file"""

    name: str
    indicator_description: str
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

    label: str
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
        self.bpolys = bpolys
        self.dataset = dataset
        self.feature_id = feature_id
        if bpolys is None and dataset and feature_id:
            self.bpolys = get_bpolys_from_db(self.dataset, self.feature_id)
        else:
            raise ValueError(
                "Provide either a bounding polygone"
                + "or dataset name and feature id as parameter."
            )
        # setattr(object, key, value) could be used instead of relying on from_dict.
        metadata = get_indicator_metadata(type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)

        layer = get_layer_definition(layer_name)
        self.layer: LayerDefinition = from_dict(data_class=LayerDefinition, data=layer)

        random_id = str(uuid.uuid1())
        filename = "_".join([self.metadata.name, self.layer.name, random_id, ".svg"])
        figure_path = os.path.join(DATA_PATH, filename)

        self.result: Result = Result(None, None, None, figure_path)

    def get(self) -> Tuple[Result, Metadata]:
        """Pass the indicator results to the user.

        For dynamic indicators this will trigger the processing.
        For non-dynamic (pre-processed) indicators this will
        extract the results from the geo database.
        """
        if self.dynamic:
            logger.info(f"Run processing for dynamic indicator {self.name}.")
            result = self.run_processing()
        else:
            logger.info(
                f"Get pre-processed results from geo db for indicator {self.name}."
            )
            result = self.get_from_database()
        return result, self.metadata

    def save_to_database(self) -> None:
        """Save the results to the geo database."""
        save_indicator_results_to_db(
            dataset=self.dataset,
            feature_id=self.feature_id,
            layer_name=self.layer.name,
            indicator=self.metadata.name,
            results=self.result,
        )

    def get_from_database(self) -> Result:
        """Get pre-processed indicator results from geo database."""
        result = get_indicator_results_from_db(
            dataset=self.dataset,
            feature_id=self.feature_id,
            layer_name=self.layer.name,
            indicator=self.metadata.name,
        )
        return result

    @abstractmethod
    def preprocess(self) -> None:
        pass

    @abstractmethod
    def calculate(self) -> None:
        pass

    @abstractmethod
    def create_figure(self) -> None:
        pass
