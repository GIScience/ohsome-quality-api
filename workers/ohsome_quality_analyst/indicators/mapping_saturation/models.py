"""Model Classes.

The classes includes methods with the function formular, for making an initial guess
of the parameters and getting boundaries of the parameters."""

from abc import ABC, abstractmethod

import numpy as np


class Model(ABC):
    """The Base Class of every model."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def function_formula(self) -> str:
        pass

    # Alternative names could be: `function` or `y`
    @abstractmethod
    def function():
        """The function definition."""
        pass

    @abstractmethod
    def get_initial_guess():
        """Get an initial fuess on the parameters."""
        pass

    @abstractmethod
    def get_bounds():
        """Get lower and upper bounds of the parameters."""
        pass


class Sigmoid(Model):
    """Sigmoid model."""

    name = "Sigmoid model"
    function_formula = ""

    def function(self, x: float, x_0: float, k: float, L: float):
        """Sigmoid function.

        Fuction formula is taken from the Wikipedia article "Logistic function":
        https://en.wikipedia.org/wiki/Logistic_function

        Args:
            L: the curve's maximum value/asymptotic (the plateaus).
            k: the Logistic growth rate or steepness of the curve.
            x_0: the x value of the sigmoid's midpoint (inflection point).
        """
        return L / (1 + np.exp(-k * (x - x_0)))

    def get_initial_guess(self, xdata: np.ndarray, ydata: np.ndarray) -> tuple:
        """Get an initial guess on parameters for single Sigmoid function."""
        x_0 = xdata.size / 2
        k = 0
        L = ydata.max()
        return (x_0, k, L)

    def get_bounds(self, xdata: np.ndarray, ydata: np.ndarray) -> tuple:
        """Get lower and upper bounds of the parameters for single Sigmoid function."""
        x_0_upper_bound = xdata.size * 1.5
        x_0_lower_bound = 0.0
        k_upper_bound = 1.0
        k_lower_bound = -1.0
        L_upper_bound = ydata.max()
        L_lower_bound = 0.0
        return (
            (x_0_lower_bound, k_lower_bound, L_lower_bound),
            (x_0_upper_bound, k_upper_bound, L_upper_bound),
        )


class SSlogis(Model):
    """Self-Starting Nls Logistic Model."""

    name = "Self-Starting Nls Logistic Model"
    function_formula = ""

    def function(self, x, asym, xmid, scal):
        """SSlogis function.

        Function formula and parameter description taken from R Documentation:
        "SSlogis: Self-Starting Nls Logistic Model":
        https://rdrr.io/r/stats/SSlogis.html

        Args:
            x: a numeric vector of values at which to evaluate the model.
            asym: a numeric parameter representing the asymptote.
            xmid: a numeric parameter representing the x value at the inflection point
                of the curve. The value of SSlogis will be Asym/2 at xmid.
            scal: a numeric scale parameter on the input axis.

        """
        return asym / (1 + np.exp((xmid - x) / scal))

    def get_initial_guess(self):
        """Get an initial fuess on the parameters."""
        raise NotImplementedError

    def get_bounds(self):
        """Get lower and upper bounds of the parameters."""
        raise NotImplementedError


class SSfpl:
    """Self-Starting Nls Four-Parameter Logistic Model."""

    name = "Self-Starting Nls Four-Parameter Logistic Model"
    function_formula = ""

    def function(self, x, A, B, xmid, scal):
        """SSfpl function.

        Function formula and parameter description taken from R Documentation
        "SSfpl: Self-Starting Nls Four-Parameter Logistic Model":
        https://rdrr.io/r/stats/SSfpl.html

        Args:
            x: a numeric vector of values at which to evaluate the model.
            A: A numeric parameter representing the horizontal asymptote on the left
                side (very small values of x).
            B: A numeric parameter representing the horizontal asymptote on the right
                side (very large values of x).
            xmid: A numeric parameter representing the `x` value at the inflection
                point of the curve. The value of SSfpl will be midway between A and B
                at xmid.
            scal: A numeric scale parameter on the input axis.
        """
        return A + (B - A) / (1 + np.exp((xmid - x) / scal))

    def get_initial_guess(self):
        """Get an initial fuess on the parameters."""
        raise NotImplementedError

    def get_bounds(self):
        """Get lower and upper bounds of the parameters."""
        raise NotImplementedError


class SSasymp:
    """Self-Starting Nls Asymptotic Regression Model."""

    name = "Self-Starting Nls Asymptotic Regression Model"
    function_formula = ""

    def function(self, x, asym, R0, lrc):
        """SSasymp function.

        Function formula and parameter description taken from R Documentation
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

    def get_initial_guess(self):
        """Get an initial fuess on the parameters."""
        raise NotImplementedError

    def get_bounds(self):
        """Get lower and upper bounds of the parameters."""
        raise NotImplementedError


class MichaelisMenton:
    """Michaelis-Menten model."""

    name = "Michaelis-Menten model"
    function_formula = ""

    def function(self, x, Vmax, Km):
        """Michaelis-Menten function.

        Function formula is taken from the Wikipedia article
        "Michaelis–Menten kinetics":
        https://en.wikipedia.org/wiki/Michaelis%E2%80%93Menten_kinetics

        Args:
            Vmax: the curve's maximum value/asymptotic
            Km: Michaelis constant
        """
        return Vmax * x / (Km + x)

    def get_initial_guess(self):
        """Get an initial fuess on the parameters."""
        raise NotImplementedError

    def get_bounds(self):
        """Get lower and upper bounds of the parameters."""
        raise NotImplementedError


# def sigmoid_1(x, x_01, k1, L1):
#     """Alias for the `sigmoid` function."""
#     return sigmoid(x, x_01, k1, L1)


# # fmt: off
# def sigmoid_2(x, x_01, x_02, k1, k2, L1, L2):
#     """Sigmoid with 2 jumps."""
#     _L2 = L2 - L1
#     return (
#         sigmoid(x, x_01, k1, L1)
#         + sigmoid(x, x_02, k2, _L2)
#     )


# def sigmoid_3(x, x_01, x_02, x_03, k1, k2, k3, L1, L2, L3):
#     """Sigmoid with 3 jumps."""
#     _L3 = L3 - L2
#     _L2 = L2 - L1
#     return (
#         sigmoid(x, x_01, k1, L1)
#         + sigmoid(x, x_02, k2, _L2)
#         + sigmoid(x, x_03, k3, _L3)
#     )


# def sigmoid_4(x, x_01, x_02, x_03, x_04, k1, k2, k3, k4, L1, L2, L3, L4):
#     """Sigmoid with 3 jumps."""
#     _L4 = L4 - L3
#     _L3 = L3 - L2
#     _L2 = L2 - L1
#     return (
#         sigmoid(x, x_01, k1, L1)
#         + sigmoid(x, x_02, k2, _L2)
#         + sigmoid(x, x_03, k3, _L3)
#         + sigmoid(x, x_04, k4, _L4)
#     )
# # fmt: on
