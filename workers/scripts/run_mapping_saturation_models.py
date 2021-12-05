"""Run all statistical models of the Mapping Saturation indicator and plot them."""

import matplotlib.pyplot as plt
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation.fit import run_all_models
from tests.unittests.mapping_saturation.fixtures import VALUES


def main():
    xdata = np.asarray(range(len(VALUES)))
    ydata = VALUES
    fitted_models = run_all_models(xdata, ydata)
    plt.figure()
    prev_ax = None
    for i, model in enumerate(fitted_models):
        if i == 0:
            ax = plt.subplot(2, 3, i + 1)
        else:
            ax = plt.subplot(2, 3, i + 1, sharex=prev_ax, sharey=prev_ax)
        ax.plot(xdata, ydata)
        ax.plot(
            xdata,
            model.fitted_values,
            label="{0}: {1}".format(model.metric_name, model.metric),
        )
        ax.axhline(y=model.asymptote, color="pink", linestyle="--", label="Asymptote")
        ax.set_title(model.model_name)
        ax.legend()
        ax.set(xlabel="x-label", ylabel="y-label")
        ax.label_outer()
        prev_ax = ax
    plt.show()


if __name__ == "__main__":
    main()
