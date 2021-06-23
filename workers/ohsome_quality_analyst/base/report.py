import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from statistics import mean
from typing import Dict, List, Literal, NamedTuple, Tuple

from dacite import from_dict
from geojson import FeatureCollection

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.utils.definitions import get_metadata


@dataclass
class Metadata:
    """Metadata of an report as defined in the metadata.yaml file"""

    name: str
    description: str
    label_description: Dict


@dataclass
class Result:
    """The result of the Report."""

    label: Literal["green", "yellow", "red", "undefined"]
    value: float
    description: str


class IndicatorLayer(NamedTuple):
    indicator_name: str
    layer_name: str


class BaseReport(metaclass=ABCMeta):
    """Subclass has to create and append indicator objects to indicators list."""

    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        fid_field: str = None,
    ):
        self.dataset = dataset
        self.feature_id = feature_id
        self.fid_field = fid_field
        self.bpolys = bpolys

        # Definies indicator+layer combinations
        self.indicator_layer: Tuple[IndicatorLayer] = []
        self.indicators: List[BaseIndicator] = []

        metadata = get_metadata("reports", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)
        # Results will be written during the lifecycle of the report object (combine())
        self.result = Result(None, None, None)

    @abstractmethod
    def set_indicator_layer(self) -> None:
        """Set the attribute indicator_layer."""
        pass

    @abstractmethod
    def combine_indicators(self) -> None:
        """Combine indicators results and create the report result object."""
        logging.info(f"Combine indicators for report: {self.metadata.name}")

        values = []
        for indicator in self.indicators:
            if indicator.result.label != "undefined":
                values.append(indicator.result.value)

        if not values:
            self.result.value = None
            self.result.label = "undefined"
            self.result.description = "Could not derive quality level"
            return None
        else:
            self.result.value = mean(values)

        if self.result.value < 0.5:
            self.result.label = "red"
            self.result.description = self.metadata.label_description["red"]
        elif self.result.value < 1:
            self.result.label = "yellow"
            self.result.description = self.metadata.label_description["yellow"]
        elif self.result.value >= 1:
            self.result.label = "green"
            self.result.description = self.metadata.label_description["green"]
