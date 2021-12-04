"""Model Classes.

These classes include methods with the function formula and for fitting data to this
function formula.
"""

from abc import ABC, abstractmethod

import numpy as np
from rpy2 import robjects
from scipy.optimize import curve_fit


class Model(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def function_formula(self) -> str:
        pass

    @abstractmethod
    def function() -> np.float64:
        pass

    # TODO: Should this function return coef and fitted data?
    # In this case `fitted.values(object, …)` in R can be used.
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

    # TODO: Should there be checks for input data?
    # Where should they be called? During __init__()?
    def check_xy_data(self, xdata, ydata):
        assert np.shape(xdata) == np.shape(ydata)


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
        # curve_fit: Use non-linear least squares to fit a function, f, to data.
        # popt: Optimal values for the parameters as array
        popt, _ = curve_fit(
            self.function,
            xdata=xdata,
            ydata=ydata,
            p0=self.initial_guess(xdata, ydata),
            bounds=self.bounds(xdata, ydata),
        )
        return {"x_0": popt[0], "k": popt[1], "L": popt[2]}

    def initial_guess(self, xdata, ydata) -> tuple:
        """Get an initial guess on parameters for single Sigmoid function."""
        x_0 = xdata.size / 2
        k = 0
        L = ydata.max()
        return (x_0, k, L)

    def bounds(self, xdata, ydata) -> tuple:
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


class DoubleSigmoid(Model):
    # TODO: Should this model based on previous model (Sigmoid) be implemented?
    # function_formula:
    # (L / (1 + np.exp(-k * (x - x_0))))
    # + (L2 / 1 + np.exp(-k2 * (x - x_02)))
    pass


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

    def function(self, x, asym, xmid, scal):
        return asym / (1 + np.exp((xmid - x) / scal))

    def fit(self, xdata, ydata):
        # R environments can be described as an hybrid of a dictionary and a scope.
        robjects.globalenv["x"] = robjects.FloatVector(xdata)
        robjects.globalenv["y"] = robjects.FloatVector(ydata)
        # The string passed to the call of the robject `r` is evaluated as R code.
        raw_coef = robjects.r(
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


class SSdoubleS:
    """Two-Steps-Sigmoidal Model (Tangens Hyperbolicus)

    Function Formula:

        e + (f - e) * 1 / 2 * (np.tanh(k * (x - b)) + 1)
        + (Z - f) * 1 / 2 * (np.tanh(k * (x - c)) + 1)
    """

    name = "Two-Steps-Sigmoidal Model (Tangens Hyperbolicus)"
    function_formula = (
        "e + (f - e) * 1 / 2 * (np.tanh(k * (x - b)) + 1)"
        + "+ (Z - f) * 1 / 2 * (np.tanh(k * (x - c)) + 1)"
    )

    def function(self, x, e, f, k, b, Z, c):
        return (
            e
            + (f - e) * 1 / 2 * (np.tanh(k * (x - b)) + 1)
            + (Z - f) * 1 / 2 * (np.tanh(k * (x - c)) + 1)
        )
        pass

    def fit(self, xdata, ydata):
        # curve_fit: Use non-linear least squares to fit a function, f, to data.
        # popt: Optimal values for the parameters as array
        popt, _ = curve_fit(
            self.function,
            xdata=xdata,
            ydata=ydata,
            p0=self.initial_guess(xdata, ydata),
            # TODO: Do we need to define the bounds here?`Will they improve the fit?
            # bounds=self.bounds()
        )
        return {
            "e": popt[0],
            "f": popt[1],
            "k": popt[2],
            "b": popt[3],
            "Z": popt[4],
            "c": popt[5],
        }

    def initial_guess(self, xdata, ydata):
        e = ydata.min()
        f = ydata.max() / 2.0
        k = 10.0
        # TODO: Here multiple indicies matching the condition exists.
        # Which one should be chosen?
        # In R following code has been used: b <- x[which.min(y)]
        (indicies,) = np.where(np.isclose(ydata, np.min(ydata)))
        b = xdata[indicies[0]]
        Z = ydata.max()
        c = xdata.max() * 0.5
        return (e, f, k, b, Z, c)

    def bounds(self, xdata, ydata):
        # TODO: Remove if not needed
        raise NotImplementedError


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

    def fit(self, xdata, ydata):
        robjects.globalenv["x"] = robjects.FloatVector(xdata)
        robjects.globalenv["y"] = robjects.FloatVector(ydata)
        raw_coef = robjects.r(
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

    def fit(self, xdata, ydata):
        robjects.globalenv["x"] = robjects.FloatVector(xdata)
        robjects.globalenv["y"] = robjects.FloatVector(ydata)
        raw_coef = robjects.r(
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


class SSmicmen:
    """Self-Starting Nls Michaelis-Menten Model

    Function Formula

        Vm * x / (K + x)

    Parameters

        Vm, numeric parameter representing the maximum value of the response
            (the curve's maximum value/asymptotic);

        K, numeric parameter representing the input value at which half the maximum
            response is attained (Michaelis constant);

    Function formula and parameter description is taken from the R documentation
    "SSmicmen: Self-Starting Nls Michaelis-Menten Model":
    https://rdrr.io/r/stats/SSmicmen.html
    """

    name = "Self-Starting Nls Michaelis-Menten Model"
    function_formula = "Vm * x / (K + x)"

    def function(self, x, Vm, K):
        return Vm * x / (K + x)

    def fit(self, xdata, ydata):
        robjects.globalenv["x"] = robjects.FloatVector(xdata)
        robjects.globalenv["y"] = robjects.FloatVector(ydata)
        raw_coef = robjects.r(
            """
        df <- data.frame(x, y)
        fm <- nls(y ~ SSmicmen(x, Vm, K), data = df)
        coef(fm)
        """
        )
        return {
            "Vm": raw_coef[0],
            "K": raw_coef[1],
        }
