from typing import List

import matplotlib.pyplot as plt


def create_figure(values: list, ydata: List[list], ax_titles=[], fig_title="") -> None:
    """Create svg with data line in blue and sigmoid curve in red."""
    fig, axs = plt.subplots(len(ydata))
    fig.suptitle(fig_title)

    xdata = list(range(len(values)))
    for i, ax in enumerate(axs):
        # plot the data
        ax.set_title(ax_titles[i])
        ax.plot(
            xdata,
            values,
            label="OSM data",
        )
        # plot sigmoid curves
        ax.plot(
            xdata,
            ydata[i],
            label="Sigmoid curve",
        )
    plt.show()
    # plt.savefig(fig_title + ".png")
