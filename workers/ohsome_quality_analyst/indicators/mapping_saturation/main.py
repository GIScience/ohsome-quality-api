from ohsome_quality_analyst.indicators.mapping_saturation.helpers.fixture import fixture
from ohsome_quality_analyst.indicators.mapping_saturation.helpers.plot import (
    create_figure,
)
from ohsome_quality_analyst.indicators.mapping_saturation.sigmoid_curve_2 import (
    get_best_fit,
)

if __name__ == "__main__":
    for f in fixture.values():
        ydata = f["values"]
        xdata = list(range(len(ydata)))
        ydata_opt_list = []
        best_fit = get_best_fit(xdata, ydata)
        ax_titles = ["Original"]
        ax_titles.append(best_fit.name)
        create_figure(ydata, [f["ydata"], best_fit.ydata], ax_titles, f["name"])
