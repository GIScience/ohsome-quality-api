"""Collection of common error metrics as functions."""

import numpy as np
from numpy import float64, ndarray


def me(actual: ndarray, predicted: ndarray) -> float64:
    """Mean Error"""
    return np.mean(np.subtract(actual, predicted))


def mse(actual: ndarray, predicted: ndarray) -> float64:
    """Mean Squared Error"""
    return np.mean(np.square(np.subtract(actual, predicted)))


def rmse(actual: ndarray, predicted: ndarray) -> float64:
    """Root Mean Squared Error"""
    return np.sqrt(mse(actual, predicted))


def nrmse(actual: ndarray, predicted: ndarray) -> float64:
    """Normalized Root Mean Squared Error"""
    return rmse(actual, predicted) / (actual.max() - actual.min())


def mae(actual: ndarray, predicted: ndarray) -> float64:
    """Mean Absolute Error"""
    return np.mean(np.abs(np.subtract(actual, predicted)))
