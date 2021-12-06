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
    fitted_values: ndarray


def run_all_models(xdata: ndarray, ydata: ndarray) -> List[FittedModel]:
    # TODO: Run for every model
    fitted_models = []
    for model in (
        models.Sigmoid(),
        models.SSlogis(),
        models.SSdoubleS(),
        models.SSfpl(),
        models.SSasymp(),
        models.SSmicmen(),
    ):
        coef = model.fit(xdata, ydata)
        fitted_values = model.function(xdata, **coef)
        metric = metrics.mae(ydata, fitted_values)
        fitted_models.append(
            FittedModel(
                asymptote=fitted_values.max(),
                coefficients=coef,
                function_formula=model.function_formula,
                metric=metric,
                metric_name="Mean Absolute Error",
                model_name=model.name,
                fitted_values=fitted_values,
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
