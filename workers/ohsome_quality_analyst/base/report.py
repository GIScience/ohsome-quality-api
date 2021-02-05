from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Tuple

from dacite import from_dict
from geojson import FeatureCollection

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.utils.definitions import get_metadata


@dataclass
class Metadata:
    """Metadata of an report as defined in the metadata.yaml file"""

    name: str
    report_description: str
    label_description: Dict


@dataclass
class Result:
    """The result of the Report."""

    label: str
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
    ):
        self.dataset = dataset
        self.feature_id = feature_id
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
        pass
