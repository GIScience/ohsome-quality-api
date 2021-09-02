import unittest

import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation import metrics


class TestErrors(unittest.TestCase):
    def setUp(self):
        self.actual = np.array([2, 4])
        self.predicted = np.array([4, 4])

    def test_me(self):
        result = metrics.me(self.actual, self.predicted)
        self.assertEqual(result, -1.0)
        self.assertIsInstance(result, np.float64)

    def test_rmse(self):
        result = metrics.rmse(self.actual, self.predicted)
        self.assertEqual(result, 1.4142135623730951)
        self.assertIsInstance(result, np.float64)

    def test_nrmse(self):
        result = metrics.nrmse(self.actual, self.predicted)
        self.assertEqual(result, 0.7071067811865476)
        self.assertIsInstance(result, np.float64)

    def test_mae(self):
        result = metrics.mae(self.actual, self.predicted)
        self.assertEqual(result, 1.0)
        self.assertIsInstance(result, np.float64)


if __name__ == "__main__":
    unittest.main()
