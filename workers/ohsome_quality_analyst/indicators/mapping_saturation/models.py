"""Model Classes.

The classes includes methods with the function formular, for making an initial guess
of the parameters and getting boundaries of the parameters."""

from abc import ABC, abstractmethod

import numpy as np
from rpy2.robjects import FloatVector, globalenv, r
from scipy.optimize import curve_fit


class Model(ABC):
    name: str = ""
    function_formula: str = ""

    @abstractmethod
    def function() -> np.float64:
        pass

    @abstractmethod
    def fit() -> dict:
        """Fit data to function.

        Args:
            xdata (numpy.ndarray)
            ydata (numpy.ndarray)

        Returns:
            dict: A dictionary of the coefficients with the parameter names as keys
        """
        pass


# TODO: Is this Model obsolete because of SSlogis
class Sigmoid(Model):
    """Sigmoid model.

    Function formula:

        f(x) = L / (1 + e^(-k * (x - x_0)))

    Function parameters:

        L, the curve's maximum value/asymptotic (the plateaus);
        k, the Logistic growth rate or steepness of the curve;
        x_0, the x value of the sigmoid's midpoint (inflection point);

    Function formula is taken from the Wikipedia article "Logistic function":
    https://en.wikipedia.org/wiki/Logistic_function
    """

    name = "Sigmoid model"
    function_formula = "f(x) = L / (1 + e^(-k * (x - x_0)))"

    def function(
        self, x: np.float64, x_0: np.float64, k: np.float64, L: np.float64
    ) -> np.float64:
        """Sigmoid function."""
        return L / (1 + np.exp(-k * (x - x_0)))

    def fit(self, xdata, ydata):
        # TODO: Add comments on curve_fit
        popt, pcov = curve_fit(
            self.function,
            xdata=xdata,
            ydata=ydata,
            p0=self.get_initial_guess(xdata, ydata),
            bounds=self.get_bounds(xdata, ydata),
        )
        return {"x_0": popt[0], "k": popt[1], "L": popt[2]}

    def get_initial_guess(self, x, y) -> tuple:
        """Get an initial guess on parameters for single Sigmoid function."""
        x_0 = x.size / 2
        k = 0
        L = y.max()
        return (x_0, k, L)

    def get_bounds(self, x, y) -> tuple:
        """Get lower and upper bounds of the parameters for single Sigmoid function."""
        x_0_upper_bound = x.size * 1.5
        x_0_lower_bound = 0.0
        k_upper_bound = 1.0
        k_lower_bound = -1.0
        L_upper_bound = y.max()
        L_lower_bound = 0.0
        return (
            (x_0_lower_bound, k_lower_bound, L_lower_bound),
            (x_0_upper_bound, k_upper_bound, L_upper_bound),
        )


class SSlogis(Model):
    """Self-Starting Nls Logistic Model.

    Function Formula:

        asym / (1 + e^((xmid - x) / scal))

    Function Parameters:

        x, numeric vector of values at which to evaluate the model;
        asym, numeric parameter representing the asymptote;
        xmid, numeric parameter representing the x value at the inflection point of the
            curve. The value of SSlogis will be Asym/2 at xmid;
        scal, a numeric scale parameter on the input axis;

    Function formula and parameter description taken from R Documentation:
    "SSlogis: Self-Starting Nls Logistic Model":
    https://rdrr.io/r/stats/SSlogis.html
    """

    name = "Self-Starting Nls Logistic Model"
    function_formula = "asym / (1 + e^((xmid - x) / scal))"

    def fit(self, x, y):
        # TODO: Should this function return coef and fitted data?
        # In this case `fitted.values(object, …)` in R can be used.
        # TODO: Add comments on what is going on
        globalenv["x"] = FloatVector(x)
        globalenv["y"] = FloatVector(y)
        raw_coef = r(
            """
        df <- data.frame(x, y)
        fm <- nls(y ~ SSlogis(x, Asym, xmid, scal), data = df)
        coef(fm)
        """
        )
        return {
            "asym": raw_coef[0],
            "xmid": raw_coef[1],
            "scal": raw_coef[2],
        }

    def function(self, x, asym, xmid, scal):
        return asym / (1 + np.exp((xmid - x) / scal))


class SSfpl:
    """Self-Starting Nls Four-Parameter Logistic Model.

    Function Formula:

        A + (B - A) / (1 + e^((xmid - x) / scal))

    Function Parameters:

        x, numeric vector of values at which to evaluate the model;
        A, numeric parameter representing the horizontal asymptote on the left
            side (very small values of x);
        B, numeric parameter representing the horizontal asymptote on the right
            side (very large values of x);
        xmid, numeric parameter representing the `x` value at the inflection
            point of the curve. The value of SSfpl will be midway between A and B
            at xmid;
        scal, numeric scale parameter on the input axis;

    Function formula and parameter description taken from R Documentation
    "SSfpl: Self-Starting Nls Four-Parameter Logistic Model":
    https://rdrr.io/r/stats/SSfpl.html
    """

    name = "Self-Starting Nls Four-Parameter Logistic Model"
    function_formula = "A + (B - A) / (1 + e^((xmid - x) / scal))"

    def function(self, x, A, B, xmid, scal):
        return A + (B - A) / (1 + np.exp((xmid - x) / scal))

    def fit(self, x, y):
        globalenv["x"] = FloatVector(x)
        globalenv["y"] = FloatVector(y)
        raw_coef = r(
            """
        df <- data.frame(x, y)
        fm <- nls(y ~ SSfpl(x, A, B, xmid, scal), data = df)
        coef(fm)
        """
        )
        # TODO: Check if order is right
        return {
            "A": raw_coef[0],
            "B": raw_coef[1],
            "xmid": raw_coef[2],
            "scal": raw_coef[3],
        }


class SSasymp:
    """Self-Starting Nls Asymptotic Regression Model.

    Function Formula:

        asym + (R0 - asym) * e^(-e^(lrc) * x)

    Function Parameters:

        x, numeric vector of values at which to evaluate the model;
        asym, numeric parameter representing the horizontal asymptote on the right
            side (very large values of `x`);
        R0, numeric parameter representing the response when `x` is zero;
        lrc, numeric parameter representing the natural logarithm of the rate
            constant;

    Function formula and parameter description taken from R Documentation
    "SSasymp: Self-Starting Nls Asymptotic Regression Model":
    https://rdrr.io/r/stats/SSasymp.html
    """

    name = "Self-Starting Nls Asymptotic Regression Model"
    function_formula = "asym + (R0 - asym) * e^(-e^(lrc) * x)"

    def function(self, x, asym, R0, lrc):
        return asym + (R0 - asym) * np.exp(-np.exp(lrc) * x)

    def fit(self, x, y):
        globalenv["x"] = FloatVector(x)
        globalenv["y"] = FloatVector(y)
        raw_coef = r(
            """
        df <- data.frame(x, y)
        fm <- nls(y ~ SSasymp(x, asym, R0, lrc), data = df)
        coef(fm)
        """
        )
        return {
            "asym": raw_coef[0],
            "R0": raw_coef[1],
            "lrc": raw_coef[2],
        }


class MichaelisMenton:
    """Michaelis-Menten model.

    Function Formula

        Vmax * x / (Km + x)

    Parameters

        Vmax, the curve's maximum value/asymptotic;
        Km, Michaelis constant;

    Function formula is taken from the Wikipedia article
    "Michaelis–Menten kinetics":
    https://en.wikipedia.org/wiki/Michaelis%E2%80%93Menten_kinetics
    """

    name = "Michaelis-Menten model"
    function_formula = "Vmax * x / (Km + x)"

    def function(self, x, Vmax, Km):
        return Vmax * x / (Km + x)

    def fit(self):
        raise NotImplementedError

    def get_initial_guess(self):
        """Get an initial fuess on the parameters."""
        raise NotImplementedError

    def get_bounds(self):
        """Get lower and upper bounds of the parameters."""
        raise NotImplementedError


# TODO: Remove
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
