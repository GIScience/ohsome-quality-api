from abc import ABCMeta, abstractmethod
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import logger


class BaseIndicator(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(self, dynamic: bool, bpolys: FeatureCollection) -> None:
        """Initialize an indicator"""
        # here we can put the default parameters for indicators
        # TODO: make sure that users can either pass bpolys or
        #   or specify a table in postgres to use
        self.bpolys = bpolys
        self.dynamic = dynamic
        self.results = {
            "name": self.name,
        }

    def get(self) -> Dict:
        """Pass the indicator results to the user.

        For dynamic indicators this will trigger the processing.
        For non-dynamic (pre-processed) indicators this will
        extract the results from the geo database.
        """
        if self.dynamic:
            logger.info(f"Run processing for dynamic indicator {self.name}.")
            self.run_processing()
        else:
            logger.info(
                f"Get pre-processed results from geo db for indicator {self.name}."
            )
            self.get_from_database()

        return self.results

    def run_processing(self) -> None:
        """Run all steps needed to actually compute the indicator"""
        self.preprocess()
        self.calculate()
        self.export_figures()
        logger.info(f"finished run for indicator {self.name}")

    def save_to_database(self) -> None:
        """Save the results to the geo database."""
        pass

    def get_from_database(self) -> None:
        """Get pre-processed indicator results from geo database."""
        self.results["score"] = 0.5
        pass

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
