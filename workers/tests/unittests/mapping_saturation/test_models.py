import unittest
from unittest import mock

import numpy as np
from rpy2.rinterface_lib.embedded import RRuntimeError

from ohsome_quality_analyst.indicators.mapping_saturation import models

from . import fixtures


class TestModels(unittest.TestCase):
    def setUp(self):
        self.ydata_1 = fixtures.VALUES_1
        self.xdata_1 = np.array(range(len(self.ydata_1)))
        self.ydata_2 = fixtures.VALUES_2
        self.xdata_2 = np.array(range(len(self.ydata_2)))
        self.expected_keys = [
            "name",
            "function_formula",
            "asymptote",
            "mae",
            "xdata",
            "ydata",
            "coefficients",
            "fitted_values",
        ]

    def run_tests(self, model):
        self.assertIsNotNone(model.name)
        self.assertNotEqual(model.name, "")
        self.assertIsNotNone(model.function_formula)
        self.assertNotEqual(model.function_formula, "")

        self.assertTrue(model.coefficients)
        self.assertNotEqual(model.fitted_values.size, 0)
        self.assertFalse(np.isnan(np.sum(model.fitted_values)))
        self.assertTrue(np.isfinite(np.sum(model.fitted_values)))

        self.assertIsNotNone(model.asymptote)
        self.assertIsNotNone(model.mae)
        self.assertIsNotNone(model.asym_conf_int)

        md = model.as_dict()
        self.assertListEqual(self.expected_keys, list(md.keys()))

    def test_sigmoid(self):
        model = models.Sigmoid(self.xdata_1, self.ydata_1)
        self.run_tests(model)
        model = models.Sigmoid(self.xdata_2, self.ydata_2)
        self.run_tests(model)

    def test_sslogis(self):
        model = models.SSlogis(self.xdata_1, self.ydata_1)
        self.run_tests(model)
        model = models.SSlogis(self.xdata_2, self.ydata_2)
        self.run_tests(model)

    def test_ssdoubles(self):
        with self.assertRaises(RRuntimeError):
            models.SSdoubleS(self.xdata_1, self.ydata_1)
        model = models.SSdoubleS(self.xdata_2, self.ydata_2)
        self.run_tests(model)

    def test_ssfpl(self):
        model = models.SSfpl(self.xdata_1, self.ydata_1)
        self.run_tests(model)
        with self.assertRaises(RRuntimeError):
            models.SSfpl(self.xdata_2, self.ydata_2)

    def test_ssasymp(self):
        model = models.SSasymp(self.xdata_1, self.ydata_1)
        self.run_tests(model)
        model = models.SSasymp(self.xdata_2, self.ydata_2)
        self.run_tests(model)

    def test_ssmicmen(self):
        model = models.SSmicmen(self.xdata_1, self.ydata_1)
        self.run_tests(model)
        model = models.SSmicmen(self.xdata_2, self.ydata_2)
        self.run_tests(model)

    @mock.patch.multiple(models.BaseStatModel, __abstractmethods__=set())
    def test_mae(self):
        model = models.BaseStatModel(np.array([2, 4]), np.array([2, 4]))
        model.fitted_values = np.array([4, 4])  # Mock
        result = model.mae
        self.assertEqual(result, 1.0)
        self.assertIsInstance(result, np.float64)


if __name__ == "__main__":
    unittest.main()
