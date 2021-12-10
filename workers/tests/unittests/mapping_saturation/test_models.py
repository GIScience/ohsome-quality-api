import unittest

import fixtures
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation import models


class TestModels(unittest.TestCase):
    def test_sigmoid(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.Sigmoid(xdata, ydata)

        self.assertIsNotNone(model.name)
        self.assertNotEqual(model.name, "")
        self.assertIsNotNone(model.function_formula)
        self.assertNotEqual(model.function_formula, "")

        self.assertTrue(model.coefficients)
        self.assertNotEqual(model.fitted_values.size, 0)

        self.assertIsNotNone(model.asymptote)
        self.assertIsNotNone(model.mae)

    def test_sslogis(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSlogis(xdata, ydata)

        self.assertIsNotNone(model.name)
        self.assertNotEqual(model.name, "")
        self.assertIsNotNone(model.function_formula)
        self.assertNotEqual(model.function_formula, "")

        self.assertTrue(model.coefficients)
        self.assertNotEqual(model.fitted_values.size, 0)

        self.assertIsNotNone(model.asymptote)
        self.assertIsNotNone(model.mae)

    def test_ssdoubles(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSdoubleS(xdata, ydata)

        self.assertIsNotNone(model.name)
        self.assertNotEqual(model.name, "")
        self.assertIsNotNone(model.function_formula)
        self.assertNotEqual(model.function_formula, "")

        self.assertTrue(model.coefficients)
        self.assertNotEqual(model.fitted_values.size, 0)

        self.assertIsNotNone(model.asymptote)
        self.assertIsNotNone(model.mae)

    def test_ssfpl(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSlogis(xdata, ydata)

        self.assertIsNotNone(model.name)
        self.assertNotEqual(model.name, "")
        self.assertIsNotNone(model.function_formula)
        self.assertNotEqual(model.function_formula, "")

        self.assertTrue(model.coefficients)
        self.assertNotEqual(model.fitted_values.size, 0)

        self.assertIsNotNone(model.asymptote)
        self.assertIsNotNone(model.mae)

    def test_ssasymp(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSasymp(xdata, ydata)

        self.assertIsNotNone(model.name)
        self.assertNotEqual(model.name, "")
        self.assertIsNotNone(model.function_formula)
        self.assertNotEqual(model.function_formula, "")

        self.assertTrue(model.coefficients)
        self.assertNotEqual(model.fitted_values.size, 0)

        self.assertIsNotNone(model.asymptote)
        self.assertIsNotNone(model.mae)

    def test_ssmicmen(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSlogis(xdata, ydata)

        self.assertIsNotNone(model.name)
        self.assertNotEqual(model.name, "")
        self.assertIsNotNone(model.function_formula)
        self.assertNotEqual(model.function_formula, "")

        self.assertTrue(model.coefficients)
        self.assertNotEqual(model.fitted_values.size, 0)

        self.assertIsNotNone(model.asymptote)
        self.assertIsNotNone(model.mae)


if __name__ == "__main__":
    unittest.main()
