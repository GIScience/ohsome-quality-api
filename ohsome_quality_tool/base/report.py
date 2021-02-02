from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Tuple

from dacite import from_dict
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.geodatabase.client import get_bpolys_from_db
from ohsome_quality_tool.oqt import create_indicator
from ohsome_quality_tool.utils.definitions import get_metadata


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
        if bpolys is not None:
            self.bpolys = bpolys
        elif dataset is not None and feature_id is not None:
            self.bpolys = get_bpolys_from_db(self.dataset, self.feature_id)
        else:
            raise ValueError(
                "Provide either a bounding polygone "
                + "or dataset name and feature id as parameter."
            )

        # Definies indicator+layer combinations
        self.indicator_layer: Tuple[IndicatorLayer] = []
        self.indicators: List[BaseIndicator] = []
        metadata = get_metadata("reports", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)
        # Results will be written during the lifecycle of the report object (combine())
        self.result = Result(None, None, None)

    def create_indicators(self) -> None:
        """Create indicators and store them in attribute 'indicators'."""
        for indicator_name, layer_name in self.indicator_layer:
            self.indicators.append(
                create_indicator(
                    indicator_name,
                    layer_name,
                    self.bpolys,
                    self.dataset,
                    self.feature_id,
                )
            )

    @abstractmethod
    def set_indicator_layer(self) -> None:
        """Set the attribute indicator_layer."""
        pass

    @abstractmethod
    def combine_indicators(self) -> None:
        """Combine indicators results and create the report result object."""
        pass
