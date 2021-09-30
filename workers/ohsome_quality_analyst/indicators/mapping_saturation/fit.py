"""Fit sigmoid functions to data.

Nonlinear least squares optimization is used to fit data to sigmoid functions which
include up to four jumps.

Best fitting function is chosen by the applying mean-squared error criterion.
"""

import logging
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.optimize import curve_fit

from ohsome_quality_analyst.indicators.mapping_saturation import sigmoid_curves


@dataclass
class Fit:
    func_name: str
    ydata: list
    mse: float


def get_best_fit(xdata: list, ydata: list) -> Fit:
    """Get best fit function based on Mean Squared Error.

    Fit sigmoid_1 to sigmoid_4 to given data and return best fit based on Mean Squared
    Error.
    """
    best_fit = None
    # For sigmoid_1 to sigmoid_4
    for i in range(1, 5):
        func_name = "sigmoid_" + str(i)
        func = getattr(sigmoid_curves, func_name)
        p0 = get_initial_guess(i, xdata, ydata)
        bounds = get_bounds(i, xdata, ydata)
        try:
            # curve_fit: Use non-linear least squares to fit a function, f, to data.
            # popt: Optimal values for the parameters as array
            # pcov: The estimated covariance of popt as 2-D array
            popt, pcov = curve_fit(func, xdata=xdata, ydata=ydata, p0=p0, bounds=bounds)
        except RuntimeError as err:
            # Optimal parameters not found:
            #   The maximum number of function evaluations is exceeded.
            logging.warning(err)
            continue
        ydata_fitted = func(xdata, *popt)
        mse = calc_mse(ydata, ydata_fitted)
        fit = Fit(func_name, ydata_fitted, mse)
        if best_fit is None or best_fit.mse > fit.mse:
            best_fit = fit
    return best_fit


def get_initial_guess(n: int, xdata: list, ydata: list) -> tuple:
    """Make initial guess on parameters for sigmoid function(s).

    Args:
        n: Number of sigmoid functions to combine. Should be 1, 2, 3 or 4.
          Single sigmoid has n=1.
          Double sigmoid has n=2.
    """
    x_0 = []
    k = []
    L = []  # noqa: N806 NOSONAR
    for i in range(n):
        x_0.append((len(xdata) / (n + 1) * (i + 1)))
        k.append(0)
        L.append((max(ydata) / n) * (i + 1))
    return tuple(x_0 + k + L)


def get_bounds(n: int, xdata: list, ydata: list) -> Tuple[Tuple[float], Tuple[float]]:
    """Get lower and upper bounds on parameters for sigmoid function(s).

    Args:
        n: Number of sigmoid functions to combine. Should be 1, 2, 3 or 4.
          Single sigmoid has n=1.
          Double sigmoid has n=2.

    Returns:
        tuple: Returns bounds on parameters.

        Each element of the tuple is an list with the length equal to the number
        of parameters.
    """
    x_0_upper_bounds = [len(xdata) * 1.5] * n
    x_0_lower_bounds = [0.0] * n
    k_upper_bounds = [1.0] * n
    k_lower_bounds = [-1.0] * n
    L_upper_bounds = [  # noqa: N806 NOSONAR
        (max(ydata) / n) * (i + 1.0) for i in range(n)
    ]
    L_lower_bounds = [0.0] * n  # noqa: N806 NOSONAR
    return (
        tuple(x_0_lower_bounds + k_lower_bounds + L_lower_bounds),
        tuple(x_0_upper_bounds + k_upper_bounds + L_upper_bounds),
    )


def calc_mse(a: list, b: list) -> float:
    """Calculate Mean Squared Error"""
    return np.square(np.subtract(a, b)).mean()
