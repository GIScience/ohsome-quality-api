from abc import ABCMeta, abstractmethod
from typing import Dict, Tuple

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import ReportMetadata, ReportResult, logger
from ohsome_quality_tool.utils.geodatabase import get_bpolys_from_db


class BaseReport(metaclass=ABCMeta):
    """The base class for all reports."""

    def __init__(
        self,
        dynamic: bool,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ):
        """Initialize a report"""
        # here we can put the default parameters for reports
        self.dynamic = dynamic

        if self.dynamic:
            if bpolys is None:
                raise ValueError
            # for dynamic calculation you need to provide geojson geometries
            self.bpolys = bpolys
        else:
            if dataset is None or feature_id is None:
                raise ValueError
            # for static calculation you need to provide the dataset name and
            # optionally an feature_id string, e.g. which geometry ids to use
            self.dataset = dataset
            self.feature_id = feature_id
            self.bpolys = get_bpolys_from_db(self.dataset, self.feature_id)

        self.metadata = ReportMetadata(name=self.name, description=self.description)

    def get(self) -> Tuple[ReportResult, Dict, ReportMetadata]:
        """Pass the report containing the indicator results to the user.

        For dynamic indicators this will trigger the processing.
        For non-dynamic (pre-processed) indicators this will
        extract the results from the geo database."""

        indicators = []
        for item in self.indicators_definition:
            indicator, layers = item
            if self.dynamic:
                result, metadata = indicator(
                    dynamic=True, layers=layers, bpolys=self.bpolys
                ).get()
            else:
                result, metadata = indicator(
                    dynamic=False,
                    layers=layers,
                    dataset=self.dataset,
                    feature_id=self.feature_id,
                ).get()

            indicators.append(
                {"metadata": metadata._asdict(), "result": result._asdict()}
            )

        result = self.combine_indicators(indicators)

        return result, indicators, self.metadata

    def export_as_pdf(
        self, result: ReportResult, indicators, metadata: ReportMetadata, outfile: str
    ):
        """Generate the PDF report."""
        logger.info(f"Export report as PDF for {self.name} to {outfile}")

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def indicators_definition(self):
        pass

    @abstractmethod
    def combine_indicators(self, indicators) -> ReportResult:
        """Combine indicators e.g. using a weighting schema."""
        pass
