from abc import ABCMeta


class BaseReport(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(self):
        """The function to initialize an indicator"""
        # here we can put the default parameters for reports
        pass

    def export_as_pdf(self):
        """The function to generate the PDF report."""
        pass
