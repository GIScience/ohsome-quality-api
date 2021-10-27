"""Sigmoid functions with up to four jumps."""

import numpy as np


def sigmoid(x: float, x_0: float, k: float, L: float):
    """Sigmoid function/curve.

    Three parameter logisitic limited growth function (SSlogis).

    Function definition is taken from the Wikipedia article "Logistic function":
    https://en.wikipedia.org/wiki/Logistic_function

    Args:
        L: the curve's maximum value/asymptotic (the plateaus);
        k: the Logistic growth rate or steepness of the curve
        x_0: the x value of the sigmoid's midpoint (inflection point)
    """
    return L / (1 + np.exp(-k * (x - x_0)))


def sslogis(x, asym, xmid, scal):
    """SSlogis: Self-Starting Nls Logistic Model (Sigmoid function)

    Function definition and parameter description taken from R Documentation:
    "SSlogis: Self-Starting Nls Logistic Model": https://rdrr.io/r/stats/SSlogis.html

    Args:
        x: a numeric vector of values at which to evaluate the model.
        asym: a numeric parameter representing the asymptote.
        xmid: a numeric parameter representing the x value at the inflection point of
            the curve. The value of SSlogis will be Asym/2 at xmid.
        scal: a numeric scale parameter on the input axis.

    """
    return asym / (1 + np.exp((xmid - x) / scal))


def ssfpl(x, A, B, xmid, scal):
    """Self-Starting Nls Four-Parameter Logistic Model

    Function definition and parameter description taken from R Documentation
    "SSfpl: Self-Starting Nls Four-Parameter Logistic Model":
    https://rdrr.io/r/stats/SSfpl.html

    Args:
        x: a numeric vector of values at which to evaluate the model.
        A: A numeric parameter representing the horizontal asymptote on the left side
            (very small values of x).
        B: A numeric parameter representing the horizontal asymptote on the right side
            (very large values of x).
        xmid: A numeric parameter representing the `x` value at the inflection point
            of the curve. The value of SSfpl will be midway between A and B at xmid.
        scal: A numeric scale parameter on the input axis.
    """
    return A + (B - A) / (1 + np.exp((xmid - x) / scal))


def ssasymp(x, asym, R0, lrc):
    """SSasymp: Self-Starting Nls Asymptotic Regression Model

    Function definition and parameter description taken from R Documentation
    "SSasymp: Self-Starting Nls Asymptotic Regression Model":
    https://rdrr.io/r/stats/SSasymp.html

    Args:
        x: a numeric vector of values at which to evaluate the model.
        asym: a numeric parameter representing the horizontal asymptote on the right
            side (very large values of `x`).
        R0: a numeric parameter representing the response when `x` is zero.
        lrc: a numeric parameter representing the natural logarithm of the rate
            constant.
    """
    return asym + (R0 - asym) * np.exp(-np.exp(lrc) * x)


def michaelis_menton(x, Vmax, Km):
    """Michaelis-Menten equation.

    Function definition is taken from the Wikipedia article "Michaelis–Menten kinetics":
    https://en.wikipedia.org/wiki/Michaelis%E2%80%93Menten_kinetics

    Args:
        Vmax: the curve's maximum value/asymptotic
        Km: Michaelis constant
    """
    return Vmax * x / (Km + x)


def sigmoid_1(x, x_01, k1, L1):
    """Alias for the `sigmoid` function."""
    return sigmoid(x, x_01, k1, L1)


# fmt: off
def sigmoid_2(x, x_01, x_02, k1, k2, L1, L2):
    """Sigmoid with 2 jumps."""
    _L2 = L2 - L1
    return (
        sigmoid(x, x_01, k1, L1)
        + sigmoid(x, x_02, k2, _L2)
    )


def sigmoid_3(x, x_01, x_02, x_03, k1, k2, k3, L1, L2, L3):
    """Sigmoid with 3 jumps."""
    _L3 = L3 - L2
    _L2 = L2 - L1
    return (
        sigmoid(x, x_01, k1, L1)
        + sigmoid(x, x_02, k2, _L2)
        + sigmoid(x, x_03, k3, _L3)
    )


def sigmoid_4(x, x_01, x_02, x_03, x_04, k1, k2, k3, k4, L1, L2, L3, L4):
    """Sigmoid with 3 jumps."""
    _L4 = L4 - L3
    _L3 = L3 - L2
    _L2 = L2 - L1
    return (
        sigmoid(x, x_01, k1, L1)
        + sigmoid(x, x_02, k2, _L2)
        + sigmoid(x, x_03, k3, _L3)
        + sigmoid(x, x_04, k4, _L4)
    )
# fmt: on
