from abc import ABCMeta, abstractmethod

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import logger


class BaseReport(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(self, bpolys: FeatureCollection):
        """Initialize a report"""
        # here we can put the default parameters for reports
        self.bpolys = bpolys

    def run(self):
        self.calculate_indicators()
        self.combine_indicators()
        self.export_as_pdf()

    def calculate_indicators(self):
        """Calculate all indicators provided for this report."""
        logger.info(f"Calculate individual indicators for {self.name}")
        logger.info(f"indicators: {self.indicators}")
        for i, indicator in enumerate(self.indicators):
            indicator.constructor(bpolys=self.bpolys).run()

    def export_as_pdf(self):
        """Generate the PDF report."""
        logger.info(f"Export report as PDF for {self.name}")

    @abstractmethod
    def combine_indicators(self):
        """Combine indicators e.g. using a weighting schema."""
        pass
