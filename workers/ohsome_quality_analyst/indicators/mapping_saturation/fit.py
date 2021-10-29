"""Fit models to data and choose best fit based on Mean Absolute Error."""


from dataclasses import dataclass

from numpy import float64, ndarray

from ohsome_quality_analyst.indicators.mapping_saturation import metrics, models


# TODO: What should the attributes be?
@dataclass
class Fit:
    asymptote: float64
    coefficients: dict
    function_formula: str
    metric: float64
    metric_name: str
    model_name: str
    ydata: ndarray


def get_best_fit(xdata: ndarray, ydata: ndarray) -> Fit:
    """Fit models to data and return best fit based on Mean Absolute Error."""
    best_fit: Fit = None
    # TODO: Run for every model
    for model in (models.Sigmoid(), models.SSlogis(), models.SSfpl(), models.SSasymp()):
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
        if best_fit is None or best_fit.metric > fit.metric:
            best_fit = fit
        return best_fit
