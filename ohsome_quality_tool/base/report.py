from abc import ABCMeta, abstractmethod


class BaseReport(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(self):
        """Initialize a report"""
        # here we can put the default parameters for reports
        pass

    def export_as_pdf(self):
        """Generate the PDF report."""
        pass

    @abstractmethod
    def calculate(self):
        pass
