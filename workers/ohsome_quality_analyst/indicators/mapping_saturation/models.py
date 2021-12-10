"""Statistical Model Classes"""

import os
from abc import ABC, abstractmethod

import numpy as np
import rpy2.robjects.packages as rpackages
from rpy2 import robjects
from scipy.optimize import curve_fit

from ohsome_quality_analyst.indicators.mapping_saturation import metrics


class BaseStatModel(ABC):
    """Base Statistical Model"""

    def __init__(self, xdata: np.ndarray, ydata: np.ndarray):
        assert np.shape(xdata) == np.shape(ydata)
        self.xdata = xdata
        self.ydata = ydata
        self.coefficients = {}
        self.fitted_values = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the statistical model"""
        pass

    @property
    @abstractmethod
    def function_formula(self) -> str:
        """Function formular of the statistical model"""
        pass

    @property
    @abstractmethod
    def asymptote(self) -> str:
        pass

    @property
    def mae(self) -> str:
        """Mean absolute error"""
        return metrics.mae(self.ydata, self.fitted_values)


class BaseStatModelR(BaseStatModel):
    """Base Statistical Model using R"""

    rstats = rpackages.importr("stats")

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        robjects.globalenv["x"] = robjects.FloatVector(self.xdata)
        robjects.globalenv["y"] = robjects.FloatVector(self.ydata)


class Sigmoid(BaseStatModel):
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

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        # curve_fit: Use non-linear least squares to fit a function, f, to data.
        # popt: Optimal values for the parameters as array
        popt, _ = curve_fit(
            self.function,
            xdata=xdata,
            ydata=ydata,
            p0=self.initial_guess(),
            bounds=self.bounds(),
        )
        self.coefficients = {"x_0": popt[0], "k": popt[1], "L": popt[2]}
        self.fitted_values = self.function(xdata, **self.coefficients)

    def function(
        self, x: np.float64, x_0: np.float64, k: np.float64, L: np.float64
    ) -> np.float64:
        """Sigmoid function."""
        return L / (1 + np.exp(-k * (x - x_0)))

    def initial_guess(self) -> tuple:
        """Get an initial guess on parameters for single Sigmoid function."""
        x_0 = self.xdata.size / 2
        k = 0
        L = self.ydata.max()
        return (x_0, k, L)

    def bounds(self) -> tuple:
        """Get lower and upper bounds of the parameters for single Sigmoid function."""
        x_0_upper_bound = self.xdata.size * 1.5
        x_0_lower_bound = 0.0
        k_upper_bound = 1.0
        k_lower_bound = -1.0
        L_upper_bound = self.ydata.max()
        L_lower_bound = 0.0
        return (
            (x_0_lower_bound, k_lower_bound, L_lower_bound),
            (x_0_upper_bound, k_upper_bound, L_upper_bound),
        )

    @property
    def asymptote(self):
        return self.coefficients["L"]


class SSdoubleS(BaseStatModelR):
    """Two-Steps-Sigmoidal Model (Tangens Hyperbolicus)

    Function Formula:

        e + (f - e) * 1 / 2 * (np.tanh(k * (x - b)) + 1)
        + (Z - f) * 1 / 2 * (np.tanh(k * (x - c)) + 1)

    Function parameters:
        Z, numeric parameter representing the asymptote;
    """

    name = "Two-Steps-Sigmoidal Model (Tangens Hyperbolicus)"
    function_formula = (
        "e + (f - e) * 1 / 2 * (np.tanh(k * (x - b)) + 1)"
        + "+ (Z - f) * 1 / 2 * (np.tanh(k * (x - c)) + 1)"
    )

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "ssdoubles.R"),
            "r",
        ) as file:
            robjects.r(file.read())
        fitted_model = self.rstats.nls("y ~ SSdoubleS(x, e, f, k, b, Z, c)")
        coef = np.asarray(self.rstats.coef(fitted_model))
        self.coefficients = {
            "e": coef[0],
            "f": coef[1],
            "k": coef[2],
            "b": coef[3],
            "Z": coef[4],
            "c": coef[5],
        }
        self.fitted_values = np.asarray(self.rstats.fitted(fitted_model))

    @property
    def asymptote(self):
        return self.coefficients["Z"]


class SSlogis(BaseStatModelR):
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

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        fitted_model = self.rstats.nls("y ~ SSlogis(x, Asym, xmid, scal)")
        coef = np.asarray(self.rstats.coef(fitted_model))
        self.coefficients = {
            "Asym": coef[0],
            "xmid": coef[1],
            "scal": coef[2],
        }
        self.fitted_values = np.asarray(self.rstats.fitted(fitted_model))

    @property
    def asymptote(self):
        return self.coefficients["Asym"]


class SSfpl(BaseStatModelR):
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

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        fitted_model = self.rstats.nls("y ~ SSfpl(x, A, B, xmid, scal)")
        coef = np.asarray(self.rstats.coef(fitted_model))
        self.coefficients = {
            "A": coef[0],
            "B": coef[1],
            "xmid": coef[2],
            "scal": coef[3],
        }
        self.fitted_values = np.asarray(self.rstats.fitted(fitted_model))

    @property
    def asymptote(self):
        return self.coefficients["B"]


class SSasymp(BaseStatModelR):
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

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        fitted_model = self.rstats.nls("y ~ SSasymp(x, asym, R0, lrc)")
        coef = np.asarray(self.rstats.coef(fitted_model))
        self.coefficients = {
            "asym": coef[0],
            "R0": coef[1],
            "lrc": coef[2],
        }
        self.fitted_values = np.asarray(self.rstats.fitted(fitted_model))

    @property
    def asymptote(self):
        return self.coefficients["asym"]


class SSmicmen(BaseStatModelR):
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

    def __init__(self, xdata, ydata):
        # Model fails when xdata starts with zero
        if xdata[0] == 0:
            xdata = xdata + 1
        super().__init__(xdata, ydata)
        fitted_model = self.rstats.nls("y ~ SSmicmen(x, Vm, K)")
        coef = np.asarray(self.rstats.coef(fitted_model))
        self.coefficients = {
            "Vm": coef[0],
            "K": coef[1],
        }
        # Substract 1 from fitted values to adjust manipulated xdata (xdata + 1)
        self.fitted_values = np.asarray(self.rstats.fitted(fitted_model)) - 1

    @property
    def asymptote(self):
        return self.coefficients["Vm"]
