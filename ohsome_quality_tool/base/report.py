from abc import ABCMeta, abstractmethod
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.utils.config import logger
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

        self.result = {}
        self.indicators = []
        self.metadata = {
            "name": self.name,
            "description": self.description,
        }

    def get(self) -> Dict:
        """Pass the report containing the indicator results to the user.

        For dynamic indicators this will trigger the processing.
        For non-dynamic (pre-processed) indicators this will
        extract the results from the geo database."""
        for i, item in enumerate(self.indicators):
            indicator, layers = item
            if self.dynamic:
                result, metadata = indicator.constructor(
                    dynamic=self.dynamic, layers=layers, bpolys=self.bpolys
                ).get()
            else:
                results = indicator.constructor(
                    dynamic=self.dynamic,
                    layers=layers,
                    dataset=self.dataset,
                    feature_id=self.feature_id,
                ).get()
            self.indicators.append(results)

        self.combine_indicators()

        return self.result, self.metadata

    def export_as_pdf(self, outfile: str):
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
    def combine_indicators(self):
        """Combine indicators e.g. using a weighting schema."""
        pass
