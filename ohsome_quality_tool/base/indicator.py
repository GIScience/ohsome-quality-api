from abc import ABCMeta, abstractmethod

from geojson import FeatureCollection


class BaseIndicator(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(self, bpolys: FeatureCollection):
        """The function to initialize an indicator"""
        # here we can put the default parameters for indicators
        pass

    def run(self):
        self.preprocess()
        self.calculate()

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
