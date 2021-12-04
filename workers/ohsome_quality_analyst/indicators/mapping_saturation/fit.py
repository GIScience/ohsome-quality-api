"""Run all models and choose best fit based on Mean Absolute Error."""


from dataclasses import dataclass
from typing import List

from numpy import float64, ndarray

from ohsome_quality_analyst.indicators.mapping_saturation import metrics, models


@dataclass
class FittedModel:
    asymptote: float64
    coefficients: dict
    function_formula: str
    metric: float64
    metric_name: str
    model_name: str
    ydata: ndarray


def run_all_models(xdata: ndarray, ydata: ndarray) -> List[FittedModel]:
    # TODO: Run for every model
    fitted_models = []
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
        fitted_models.append(
            FittedModel(
                asymptote=ydata_fitted.max(),
                coefficients=coef,
                function_formula=model.function_formula,
                metric=metric,
                metric_name="Mean Absolute Error",
                model_name=model.name,
                ydata=ydata_fitted,
            )
        )
    return fitted_models


def get_best_fit(fitted_models: List[FittedModel]) -> FittedModel:
    best_fit: FittedModel = None
    for fit in fitted_models:
        if best_fit is None:
            best_fit = fit
        elif fit.metric < best_fit.metric:
            best_fit = fit
        else:
            continue
    return best_fit
