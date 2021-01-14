import os
import uuid
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple

import yaml
from dacite import from_dict
from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import (
    DATA_PATH,
    IndicatorMetadata,
    IndicatorResult,
    TrafficLightQualityLevels,
    logger,
)
from ohsome_quality_tool.utils.geodatabase import (
    get_bpolys_from_db,
    get_indicator_results_from_db,
    save_indicator_results_to_db,
)
from ohsome_quality_tool.utils.ohsome import client as ohsome_client


@dataclass
class Metadata:
    name: str
    indicator_description: str
    label_description: Dict
    result_description: str


@dataclass
class LayerDefinition:
    name: str
    description: str
    endpoint: str
    filter: str


@dataclass
class Result:
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
        """Initialize an indicator"""
        # here we can put the default parameters for indicators
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

        metadata = self.load_metadata()
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)

        layer = self.load_layer_definition("building_area")
        self.layer: LayerDefinition = from_dict(data_class=LayerDefinition, data=layer)

        random_id = uuid.uuid1()
        filename = "_".join([self.metadata.name, self.layer.name, random_id, ".svg"])
        self.figure = os.path.join(DATA_PATH, filename)

        self.result: Result = None

    # TODO: Does os.path.abspath(__file__) still work when implemented in parent class?
    def load_metadata(self) -> Dict:
        """Read metadata of indicator from text file."""
        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "metadata.yaml")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def load_layer_definition(self, layer_name: str) -> Dict:
        """Read layer definition from text file."""
        layer_definitions = ohsome_client.load_layer_definitions()
        return layer_definitions[layer_name]

    def get(self) -> Tuple[IndicatorResult, IndicatorMetadata]:
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

    def run_processing(self) -> IndicatorResult:
        """Run all steps needed to actually compute the indicator"""
        preprocessing_results = self.preprocess()
        label, value, text, data = self.calculate(preprocessing_results)
        svg = (
            self.create_figure(data)
            if label != TrafficLightQualityLevels.UNDEFINED
            else None
        )
        logger.info(f"finished run for indicator {self.name}")

        result = IndicatorResult(
            label=label.name,
            value=value,
            text=text,
            svg=svg,
        )

        return result

    def save_to_database(self, result: IndicatorResult) -> None:
        """Save the results to the geo database."""
        save_indicator_results_to_db(
            dataset=self.dataset,
            feature_id=self.feature_id,
            layer_name=self.layer.name,
            indicator=self.name,
            results=result,
        )

    def get_from_database(self) -> IndicatorResult:
        """Get pre-processed indicator results from geo database."""
        result = get_indicator_results_from_db(
            dataset=self.dataset,
            feature_id=self.feature_id,
            layer_name=self.layer.name,
            indicator=self.name,
        )
        return result

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    # the abstract method defines that this function
    # needs to be implemented by all children
    @abstractmethod
    def preprocess(self) -> Dict:
        pass

    @abstractmethod
    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:
        pass

    @abstractmethod
    def create_figure(self, data: Dict):
        pass
