import os
import unittest
from sklearn.model_selection import cross_validate

from ohsome_quality_analyst.indicators import building_area
from ohsome_quality_analyst.utils.helper import load_sklearn_model
import numpy as np


class TestIndicatorBuildingArea(unittest.TestCase):
    def test_model(self):
        # Model
        # Cross validation scores
        # TODO: Define range in which comparison is escapable
        r2 = 0.8447905202750137
        mse =184080026653.65894
        mae = 213554.47485382063
        explained_variance = 0.8465967980937054

        # TODO: Define X and y
        X = 0
        y = 0

        path = os.path.join(
            os.path.dirname(os.path.abspath(building_area.__file__)),
            "model.joblib",
        )
        model = load_sklearn_model(path)
        scores = cross_validate(
            model,
            X,
            y,
            cv=5,
            scoring=[
                "r2",
                "neg_mean_squared_error",
                "neg_mean_absolute_error",
                "explained_variance",
            ],
        )
        r2 = np.mean(scores["test_r2"])
        mse = np.mean(scores["test_neg_mean_squared_error"]) * (-1)
        mae = np.mean(scores["test_neg_mean_absolute_error"]) * (-1)
        explained_variance = np.mean(scores["test_explained_variance"])
        # TODO: Compare with scores of GitLab repo
