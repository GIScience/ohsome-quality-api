from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, List

from dacite import from_dict
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.geodatabase.client import get_bpolys_from_db
from ohsome_quality_tool.utils.definitions import (
    ReportMetadata,
    ReportResult,
    get_metadata,
    logger,
)


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


class BaseReport(metaclass=ABCMeta):
    """Subclass has to create and append indicator objects to indicators list."""

    def __init__(
        self,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ):
        if bpolys:
            self.bpolys = bpolys
        elif self.bpolys is None and dataset and feature_id:
            self.dataset = dataset
            self.feature_id = feature_id
            self.bpolys = get_bpolys_from_db(self.dataset, self.feature_id)
        else:
            raise ValueError(
                "Provide either a bounding polygone "
                + "or dataset name and feature id as parameter."
            )

        self.indicators: List[BaseIndicator] = []
        # self.metadata = ReportMetadata(name=self.name, description=self.description)
        metadata = get_metadata("reports", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)

        # Results will be written during the lifecycle of the report object (combine())
        self.result = Result(None, None, None)

    def get(self):
        """Pass the report containing the indicator results to the user.

        For dynamic indicators this will trigger the processing.
        For non-dynamic (pre-processed) indicators this will
        extract the results from the geo database."""

        for item in self.indicators_definition:
            indicator, layer_name = item

            if self.dynamic:
                result, metadata = indicator(
                    dynamic=True, layer_name=layer_name, bpolys=self.bpolys
                ).get()
            else:
                logger.info("get static indicator values")
                result, metadata = indicator(
                    dynamic=False,
                    layer_name=layer_name,
                    dataset=self.dataset,
                    feature_id=self.feature_id,
                ).get()

            self.indicators.append(
                {"metadata": metadata._asdict(), "result": result._asdict()}
            )

        label, value, text = self.combine_indicators(self.indicators)
        self.result.label = label
        self.result.value = value
        self.result.description = text

        # return result, indicators, self.metadata

    def export_as_pdf(
        self, result: ReportResult, indicators, metadata: ReportMetadata, outfile: str
    ):
        """Generate the PDF report."""
        logger.info(f"Export report as PDF for {self.name} to {outfile}")

    # TODO: Delete
    # @property
    # @abstractmethod
    # def name(self):
    #     pass

    # @property
    # @abstractmethod
    # def description(self):
    #     pass

    @abstractmethod
    def create_indicators(self) -> None:
        """Create indicators and store them in attribute 'indicators'."""
        pass

    @abstractmethod
    def combine_indicators(self) -> None:
        """Combine indicators results and create the report result object."""
        pass
