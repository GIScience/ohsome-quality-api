import unittest

import fixtures
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation import fit


class TestFit(unittest.TestCase):
    def setUp(self):
        self.xdata = fixtures.VALUES
        self.ydata = np.asarray(range(len(fixtures.VALUES)))

    def test_get_best_fit(self):
        best_fit = fit.get_best_fit(self.xdata, self.ydata)
        self.assertIsNotNone(best_fit)
        self.assertIsInstance(best_fit, fit.Fit)


if __name__ == "__main__":
    unittest.main()
