import unittest

import fixtures
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation import fit


class TestFit(unittest.TestCase):
    def setUp(self):
        self.xdata = np.asarray(range(len(fixtures.VALUES)))
        self.ydata = fixtures.VALUES

    def test_run_all_models(self):
        fitted_models = fit.run_all_models(self.xdata, self.ydata)
        self.assertIsNotNone(fitted_models)
        self.assertIsInstance(fitted_models, list)
        self.assertIsInstance(fitted_models[0], fit.FittedModel)

    def test_get_best_fit(self):
        fitted_models = fit.run_all_models(self.xdata, self.ydata)
        f = fit.get_best_fit(fitted_models)
        self.assertIsNotNone(f)
        self.assertIsInstance(f, fit.FittedModel)


if __name__ == "__main__":
    unittest.main()
