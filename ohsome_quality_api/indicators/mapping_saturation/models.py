"""Statistical Model Classes

Some of these models are implemented and executed using R and it`s built-in stats module
. All those models are self-starting nonlinear models. Nonlinear least-squares method is
used to estimate the parameters.

The package `rpy2` is an interface to R running embedded in a Python process:
https://rpy2.github.io/

Self-starting means the model will make the initial guess. Non-linear fits are sensitive
to the initial guess. If the initial guess is not good following error can get raised by
R: "singular gradient matrix at initial parameter estimates". In this case `rpy2` will
raise an `RRuntimeError`.
"""

import os
from abc import ABC, abstractmethod

import numpy as np
import rpy2.robjects.packages as rpackages
from numpy.typing import ArrayLike, DTypeLike
from rpy2 import robjects
from scipy.optimize import curve_fit
from scipy.stats.distributions import t as t_distribution


class BaseStatModel(ABC):
    """Base Statistical Model"""

    def __init__(self, xdata: ArrayLike, ydata: ArrayLike):
        assert np.shape(xdata) == np.shape(ydata)  # noqa
        self.xdata = xdata
        self.ydata = ydata
        self.coefficients = {}
        self.fitted_values = None
        self.asym_conf_int = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the statistical model"""
        pass

    @property
    @abstractmethod
    def function_formula(self) -> str:
        """Function formula of the statistical model"""
        pass

    @property
    @abstractmethod
    def asymptote(self) -> str:
        pass

    @property
    def mae(self) -> ArrayLike | DTypeLike:
        """Mean absolute error"""
        return np.mean(np.abs(np.subtract(self.ydata, self.fitted_values)))

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in (
                "name",
                "function_formula",
                "asymptote",
                "mae",
                "xdata",
                "ydata",
                "coefficients",
                "fitted_values",
            )
        }


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
        # pcov: The estimated covariance of popt
        popt, pcov = curve_fit(
            self.function,
            xdata=xdata,
            ydata=ydata,
            p0=self.initial_guess(),
            bounds=self.bounds(),
        )

        self.coefficients = {
            "x_0": popt[0],
            "k": popt[1],
            "L": popt[2],
        }
        self.asym_conf_int = self.confint(popt, pcov)
        self.fitted_values = self.function(xdata, **self.coefficients)

    def function(
        self,
        x: ArrayLike,
        x_0: DTypeLike,
        k: DTypeLike,
        L: DTypeLike,
    ) -> ArrayLike:
        """Sigmoid function."""
        return L / (1 + np.exp(-k * (x - x_0)))

    def initial_guess(self) -> tuple:
        """Get an initial guess on parameters for single Sigmoid function."""
        x_0 = self.xdata.size / 2
        k = 0
        L = self.ydata.max(initial=0)
        return x_0, k, L

    def bounds(self) -> tuple:
        """Get lower and upper bounds of the parameters for single Sigmoid function."""
        x_0_upper_bound = self.xdata.size * 1.5
        x_0_lower_bound = 0.0
        k_upper_bound = 1.0
        k_lower_bound = -1.0
        L_upper_bound = self.ydata.max(initial=0)
        L_lower_bound = 0.0
        return (
            (x_0_lower_bound, k_lower_bound, L_lower_bound),
            (x_0_upper_bound, k_upper_bound, L_upper_bound),
        )

    @property
    def asymptote(self):
        return self.coefficients["L"]

    @property
    def inflection_point(self):
        return self.coefficients["x_0"]

    def confint(
        self,
        popt: ArrayLike,
        pcov: ArrayLike,
        par_pos: int = 2,
        level: float = 0.95,
    ) -> np.array:
        """Confidence Intervals for a certain Model Parameter

        Args:
            pcov: The estimated covariance of the optimal values for the parameters
            par_pos: Parameter position (index)
            level: Confidence level

        Returns:
            ArrayLike: lower (first element) and upper (second element) confidence
                limits of the model parameter
        """
        alpha = 1.0 - level
        # 3 is the number of parameters
        degrees_of_freedom = len(self.ydata) - 3
        tval = t_distribution.ppf(1.0 - alpha / 2.0, degrees_of_freedom)
        perr = np.sqrt(np.diag(pcov))  # standard deviation errors
        lower = popt - perr * tval
        upper = popt + perr * tval
        return np.array([lower[par_pos], upper[par_pos]])


class SSlogis(BaseStatModel):
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

    name = "Nls Logistic Model"
    function_formula = "asym / (1 + e^((xmid - x) / scal))"

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        rstats = rpackages.importr("stats")
        fmla = robjects.Formula("y ~ SSlogis(x, Asym, xmid, scal)")
        env = fmla.environment
        env["x"] = robjects.FloatVector(xdata)
        env["y"] = robjects.FloatVector(ydata)
        fm = rstats.nls(fmla)
        coef = np.array(rstats.coef(fm))
        self.coefficients = {
            "Asym": coef[0],
            "xmid": coef[1],
            "scal": coef[2],
        }
        # Confidence interval of asymptote
        self.asym_conf_int = np.array(rstats.confint(fm, "Asym", 0.95))
        self.fitted_values = np.array(rstats.fitted(fm))

    @property
    def asymptote(self):
        return self.coefficients["Asym"]

    @property
    def inflection_point(self):
        return self.coefficients["xmid"]


class SSdoubleS(BaseStatModel):
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
        if xdata.min(initial=0) == 0:
            xdata = xdata + 1
        if ydata.min(initial=0) == 0:
            ydata = ydata + 1
        rstats = rpackages.importr("stats")
        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ssdoubles.R")
        with open(fp, "r") as f:
            ssdoubles = f.read()
        robjects.r(ssdoubles)
        fmla = robjects.Formula("y ~ SSdoubleS(x, e, f, k, b, Z, c)")
        env = fmla.environment
        env["x"] = robjects.FloatVector(xdata)
        env["y"] = robjects.FloatVector(ydata)
        fm = rstats.nls(fmla)
        coef = np.array(rstats.coef(fm))
        self.coefficients = {
            "e": coef[0],
            "f": coef[1],
            "k": coef[2],
            "b": coef[3],
            "Z": coef[4],
            "c": coef[5],
        }
        self.asym_conf_int = np.array(rstats.confint(fm, "Z", 0.95))
        # Substract 1 from fitted values to adjust manipulated ydata (ydata + 1)
        self.fitted_values = np.array(rstats.fitted(fm)) - 1

    @property
    def asymptote(self):
        return self.coefficients["Z"]

    @property
    def inflection_point(self):
        return self.coefficients["f"]


class SSfpl(BaseStatModel):
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

    name = "Nls Four-Parameter Logistic Model"
    function_formula = "A + (B - A) / (1 + e^((xmid - x) / scal))"

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        rstats = rpackages.importr("stats")
        fmla = robjects.Formula("y ~ SSfpl(x, A, B, xmid, scal)")
        env = fmla.environment
        env["x"] = robjects.FloatVector(xdata)
        env["y"] = robjects.FloatVector(ydata)
        fm = rstats.nls(fmla)
        coef = np.array(rstats.coef(fm))
        self.coefficients = {
            "A": coef[0],
            "B": coef[1],
            "xmid": coef[2],
            "scal": coef[3],
        }
        self.asym_conf_int = np.array(rstats.confint(fm, "B", 0.95))
        self.fitted_values = np.array(rstats.fitted(fm))

    @property
    def asymptote(self):
        return self.coefficients["B"]

    @property
    def inflection_point(self):
        return self.coefficients["xmid"]


class SSasymp(BaseStatModel):
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

    name = "Nls Asymptotic Regression Model"
    function_formula = "asym + (R0 - asym) * e^(-e^(lrc) * x)"

    def __init__(self, xdata, ydata):
        super().__init__(xdata, ydata)
        rstats = rpackages.importr("stats")
        fmla = robjects.Formula("y ~ SSasymp(x, asym, R0, lrc)")
        env = fmla.environment
        env["x"] = robjects.FloatVector(xdata)
        env["y"] = robjects.FloatVector(ydata)
        fm = rstats.nls(fmla)
        coef = np.array(rstats.coef(fm))
        self.coefficients = {
            "asym": coef[0],
            "R0": coef[1],
            "lrc": coef[2],
        }
        self.asym_conf_int = np.array(rstats.confint(fm, "asym", 0.95))
        self.fitted_values = np.array(rstats.fitted(fm))

    @property
    def asymptote(self):
        return self.coefficients["asym"]


class SSmicmen(BaseStatModel):
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

    name = "Nls Michaelis-Menten Model"
    function_formula = "Vm * x / (K + x)"

    def __init__(self, xdata, ydata):
        # Model fails when xdata or ydata includes zero
        super().__init__(xdata, ydata)
        if xdata.min(initial=0) == 0:
            xdata = xdata + 1
        if ydata.min(initial=0) == 0:
            ydata = ydata + 1
        rstats = rpackages.importr("stats")
        fmla = robjects.Formula("y ~ SSmicmen(x, Vm, K)")
        env = fmla.environment
        env["x"] = robjects.FloatVector(xdata)
        env["y"] = robjects.FloatVector(ydata)
        fm = rstats.nls(fmla)
        coef = np.array(rstats.coef(fm))
        self.coefficients = {
            "Vm": coef[0],
            "K": coef[1],
        }
        self.asym_conf_int = np.array(rstats.confint(fm, "Vm", 0.95))
        # Substract 1 from fitted values to adjust manipulated ydata (ydata + 1)
        self.fitted_values = np.array(rstats.fitted(fm)) - 1

    @property
    def asymptote(self):
        return self.coefficients["Vm"]
