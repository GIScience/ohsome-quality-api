from abc import ABCMeta, abstractmethod


class BaseIndicator(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(self):
        """The function to initialize an indicator"""
        self.name = "test"

    def run(self):
        self.preprocess()
        self.calculate()

    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def calculate(self):
        pass
