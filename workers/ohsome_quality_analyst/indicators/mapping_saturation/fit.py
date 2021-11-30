"""Fit models to data and choose best fit based on Mean Absolute Error."""


from dataclasses import dataclass
from typing import List

from numpy import float64, ndarray

from ohsome_quality_analyst.indicators.mapping_saturation import metrics, models


@dataclass
class Fit:
    asymptote: float64
    coefficients: dict
    function_formula: str
    metric: float64
    metric_name: str
    model_name: str
    ydata: ndarray


def run_all_models(xdata: ndarray, ydata: ndarray) -> List[Fit]:
    """Fit models to data"""
    # TODO: Run for every model
    fits = []
    for model in (
        models.Sigmoid(),
        models.SSlogis(),
        models.SSdoubleS(),
        models.SSfpl(),
        models.SSasymp(),
        # models.SSmicemen(),
    ):
        coef = model.fit(xdata, ydata)
        ydata_fitted = model.function(xdata, **coef)
        metric = metrics.mae(ydata, ydata_fitted)
        fit = Fit(
            asymptote=ydata_fitted.max(),
            coefficients=coef,
            function_formula=model.function_formula,
            metric=metric,
            metric_name="Mean Absolute Error",
            model_name=model.name,
            ydata=ydata_fitted,
        )
        fits.append(fit)
        return fits


def get_best_fit(fits: List[Fit]) -> Fit:
    best_fit: Fit = None
    for fit in fits:
        if best_fit is None:
            best_fit = fit
        elif fit.metric < best_fit.metric:
            best_fit = fit
        else:
            continue
    return best_fit
