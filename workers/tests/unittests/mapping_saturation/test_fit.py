import unittest

import fixtures
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation import fit


class TestFit(unittest.TestCase):
    def setUp(self):
        self.xdata = fixtures.VALUES
        self.ydata = np.asarray(range(len(fixtures.VALUES)))

    def test_run_all_models(self):
        fits = fit.run_all_models(self.xdata, self.ydata)
        self.assertIsNotNone(fits)
        self.assertIsInstance(fits, list)
        self.assertIsInstance(fits[0], fit.Fit)

    def test_get_best_fit(self):
        fits = fit.run_all_models(self.xdata, self.ydata)
        f = fit.get_best_fit(fits)
        self.assertIsNotNone(f)
        self.assertIsInstance(f, fit.Fit)


if __name__ == "__main__":
    unittest.main()
