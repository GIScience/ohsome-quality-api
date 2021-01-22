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

from ohsome_quality_tool.utils.definitions import (
    DATA_PATH,
    get_indicator_metadata,
    get_layer_definition,
    logger,
)
from ohsome_quality_tool.utils.geodatabase import (
    get_bpolys_from_db,
    get_indicator_results_from_db,
    save_indicator_results_to_db,
)


@dataclass
class Metadata:
    """Metadata of an indicator are defined in a metadata.yaml file"""

    name: str
    indicator_description: str
    label_description: Dict
    result_description: str


@dataclass
class LayerDefinition:
    """Definitions of a layer are defined in the layer_definition.yaml file.

    The definition consist of the ohsome API Parameter needed to create the layer.
    """

    name: str
    description: str
    endpoint: str
    filter: str


@dataclass
class Result:
    """The result of and indicator."""

    label: str
    value: float
    description: str
    svg: str


class BaseIndicator(metaclass=ABCMeta):
    def __init__(
        self,
        dynamic: bool,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        self.dynamic = dynamic

        if self.dynamic:
            if bpolys is None:
                raise ValueError("Dynamic calculation requires a GeoJSON as input.")
            self.bpolys = bpolys
        else:
            if dataset is None or feature_id is None:
                raise ValueError(
                    "Static calculation requires the dataset name "
                    "and the feature id as string."
                )
            self.dataset = dataset
            self.feature_id = feature_id
            self.bpolys = get_bpolys_from_db(self.dataset, self.feature_id)

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
