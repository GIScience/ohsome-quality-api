from abc import ABCMeta, abstractmethod

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import logger


class BaseIndicator(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(self, bpolys: FeatureCollection) -> None:
        """Initialize an indicator"""
        # here we can put the default parameters for indicators
        self.bpolys = bpolys

    def run(self) -> None:
        """Run all steps to actually compute the indicator"""
        self.preprocess()
        self.calculate()
        self.export_figures()
        logger.info(f"finished run for indicator {self.name}")

    @property
    @abstractmethod
    def name(self):
        pass

    # the abstract method defines that this function
    # needs to be implemented by all children
    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def calculate(self):
        pass

    @abstractmethod
    def export_figures(self):
        pass
