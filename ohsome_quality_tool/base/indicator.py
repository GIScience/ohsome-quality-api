from abc import ABCMeta, abstractmethod
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import logger
from ohsome_quality_tool.utils.geodatabase import (
    get_bpolys_from_db,
    get_indicator_results_from_db,
)


class BaseIndicator(metaclass=ABCMeta):
    """The base class for all indicators."""

    def __init__(
        self,
        dynamic: bool,
        layers: Dict,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        """Initialize an indicator"""
        # here we can put the default parameters for indicators
        self.dynamic = dynamic
        self.layers = layers

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

    def get(self) -> Dict:
        """Pass the indicator results to the user.

        For dynamic indicators this will trigger the processing.
        For non-dynamic (pre-processed) indicators this will
        extract the results from the geo database.
        """
        if self.dynamic:
            logger.info(f"Run processing for dynamic indicator {self.name}.")
            results = self.run_processing()
        else:
            logger.info(
                f"Get pre-processed results from geo db for indicator {self.name}."
            )
            results = self.get_from_database()

        return results

    def run_processing(self) -> Dict:
        """Run all steps needed to actually compute the indicator"""
        preprocessing_results = self.preprocess()
        results = self.calculate(preprocessing_results)
        self.export_figures()
        logger.info(f"finished run for indicator {self.name}")
        return results

    def save_to_database(self) -> None:
        """Save the results to the geo database."""
        pass

    def get_from_database(self) -> Dict:
        """Get pre-processed indicator results from geo database."""
        results = get_indicator_results_from_db(
            dataset=self.dataset, feature_id=self.feature_id, indicator=self.name
        )
        return results

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
    def calculate(self, preprocessing_results: Dict):
        pass

    @abstractmethod
    def export_figures(self):
        pass
