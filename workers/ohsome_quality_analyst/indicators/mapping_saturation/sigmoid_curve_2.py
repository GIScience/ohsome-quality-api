"""TODO

In order to accommodate jumps in mapping activity
nonlinear least squares optimization is used to fit functions
which include up to four jumps superposed on a smooth sigmiond function.

Best fitting function is chosen by the applying mean-squared error criterion.
"""
from typing import Tuple

import numpy as np
from scipy.optimize import curve_fit

from ohsome_quality_analyst.indicators.mapping_saturation.helpers.fixture import fixture
from ohsome_quality_analyst.indicators.mapping_saturation.helpers.plot import (
    create_figure,
)


def sigmoid(x: float, x_0: float, k: float, L: float):
    """Sigmoid function/curve.

    Logistic function: f(x) = 1 / (1 + e^{-x})

    Args:
        L: the curve's maximum value / asymptotic (the plateaus);
        k: the logistic growth rate or steepness of the curve
        x_0: the x value of the sigmoid's midpoint
    """
    return L / (1 + np.exp(-k * (x - x_0)))


def sigmoid_1(x, x_0, k, L):
    return sigmoid(x, x_0, k, L)


# fmt: off
def sigmoid_2(x, x_01, x_02, k1, k2, L1, L2):
    """Sigmoid with 2 jumps."""
    L1 = L2 - L1
    return (
        sigmoid(x, x_01, k1, L1)
        + sigmoid(x, x_02, k2, L2)
    )


def sigmoid_3(x, x_01, x_02, x_03, k1, k2, k3, L1, L2, L3):
    """Sigmoid with 3 jumps."""
    L3 = L3 - L2
    L2 = L2 - L1
    return (
        sigmoid(x, x_01, k1, L1)
        + sigmoid(x, x_02, k2, L2)
        + sigmoid(x, x_03, k3, L3)
    )


def sigmoid_4(x, x_01, x_02, x_03, x_04, k1, k2, k3, k4, L1, L2, L3, L4):
    """Sigmoid with 3 jumps."""
    L4 = L4 - L3
    L3 = L3 - L2
    L2 = L2 - L1
    return (
        sigmoid(x, x_01, k1, L1)
        + sigmoid(x, x_02, k2, L2)
        + sigmoid(x, x_03, k3, L3)
        + sigmoid(x, x_04, k4, L4)
    )
# fmt: on


def get_initial_guess(n: int, xdata, ydata) -> tuple:
    """Make initial guess."""
    x_0 = []
    k = []
    L = []
    for i in range(n):
        x_0.append((len(xdata) / (n + 1) * (i + 1)))
        k.append(0)
        L.append((max(ydata) / n) * (i + 1))
    return x_0 + k + L


def get_bounds(n: int, xdata, ydata) -> Tuple[Tuple]:
    x_0_upper_bounds = [len(xdata) * 1.5] * n
    x_0_lower_bounds = [0] * n
    k_upper_bounds = [1] * n
    k_lower_bounds = [-1] * n
    L_upper_bounds = [(max(ydata) / n) * (i + 1)] * n
    L_lower_bounds = [0] * n
    return (
        x_0_lower_bounds + k_lower_bounds + L_lower_bounds,
        x_0_upper_bounds + k_upper_bounds + L_upper_bounds,
    )


def get_slope():
    # slope, intercept = np.polyfit(xdata, ydata, 1)
    raise NotImplementedError


def get_best_fit(xdata, ydata):
    raise NotImplementedError


if __name__ == "__main__":
    # curve_fit: Use non-linear least squares to fit a function, f, to data.
    # popt: Optimal values for the parameters as array
    # pcov: The estimated covariance of popt as 2-D array
    for f in fixture.values():
        ydata = f["values"]
        xdata = list(range(len(ydata)))
        ydata_opt_list = []
        ax_titles = ["Original"]
        for i in range(4):
            p0 = get_initial_guess(i + 1, xdata, ydata)
            bounds = get_bounds(i + 1, xdata, ydata)
            func = locals()["sigmoid_" + str(i + 1)]
            try:
                popt, pcov = curve_fit(
                    func, xdata=xdata, ydata=ydata, p0=p0, bounds=bounds
                )
            except RuntimeError as e:
                print(str(e))
                continue
            ydata_opt_list.append(func(xdata, *popt))
            ax_titles.append("sigmoid_" + str(i + 1))
        create_figure(ydata, [f["ydata"], *ydata_opt_list], ax_titles, f["name"])
