"""Run uvicorn with custom options to start API server for development purposes"""

import matplotlib.pyplot as plt
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation.fit import run_all_models
from tests.unittests.mapping_saturation.fixtures import VALUES

XDATA = np.asarray(range(len(VALUES)))
YDATA = VALUES


def run():
    fits = run_all_models(XDATA, YDATA)

    fig, axs = plt.subplots(2, 3, sharex=True, sharey=True)

    ax = axs[0, 0]
    fit = fits[0]
    plot(ax, fit)

    ax = axs[0, 1]
    fit = fits[1]
    plot(ax, fit)

    ax = axs[0, 2]
    fit = fits[2]
    plot(ax, fit)

    ax = axs[1, 0]
    fit = fits[3]
    plot(ax, fit)

    ax = axs[1, 1]
    fit = fits[4]
    plot(ax, fit)

    for ax in axs.flat:
        ax.set(xlabel="x-label", ylabel="y-label")

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axs.flat:
        ax.label_outer()

    plt.show()


def plot(ax, fit):
    ax.plot(XDATA, YDATA)
    ax.plot(XDATA, fit.ydata, label="{0}: {1}".format(fit.metric_name, fit.metric))
    ax.axhline(y=fit.asymptote, color="pink", linestyle="--", label="Asymptote")
    ax.set_title(fit.model_name)
    ax.legend()


if __name__ == "__main__":
    run()
