from abc import ABCMeta, abstractmethod
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import logger


class BaseReport(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(
        self,
        dynamic: bool,
        bpolys: FeatureCollection = None,
        table: str = None,
        area_filter: str = None,
    ):
        """Initialize a report"""
        # here we can put the default parameters for reports
        self.dynamic = dynamic

        if self.dynamic:
            # for dynamic calculation you need to provide geojson geometries
            self.bpolys = bpolys
        else:
            # for static calculation you need to provide the table name and
            # optionally an area_filter string, e.g. which geometry ids to use
            self.table = table
            self.area_filter = area_filter

        self.results = {"name": self.name}

    def get(self) -> Dict:
        """Pass the report containing the indicator results to the user.

        For dynamic indicators this will trigger the processing.
        For non-dynamic (pre-processed) indicators this will
        extract the results from the geo database."""
        for i, indicator in enumerate(self.indicators):
            results = indicator.constructor(
                dynamic=self.dynamic, bpolys=self.bpolys
            ).get()
            self.results[indicator] = results

        self.combine_indicators()

        return self.results

    def export_as_pdf(self, outfile: str):
        """Generate the PDF report."""
        logger.info(f"Export report as PDF for {self.name} to {outfile}")

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def indicators(self):
        pass

    @abstractmethod
    def combine_indicators(self):
        """Combine indicators e.g. using a weighting schema."""
        pass
