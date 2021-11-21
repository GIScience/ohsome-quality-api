import unittest

import fixtures
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation import models


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.ydata = fixtures.VALUES
        self.xdata = np.asarray(range(len(fixtures.VALUES)))

    def test_sigmoid(self):
        model = models.Sigmoid()
        guess = model.get_initial_guess(self.xdata, self.ydata)
        self.assertIsNotNone(guess)
        bounds = model.get_bounds(self.xdata, self.ydata)
        self.assertIsNotNone(bounds)
        coef = model.fit(self.xdata, self.ydata)
        self.assertIsNotNone(coef)
        y = model.function(self.xdata, **coef)
        self.assertIsNotNone(y)

    def test_sslogis(self):
        model = models.SSlogis()
        coef = model.fit(self.xdata, self.ydata)
        self.assertIsNotNone(coef)
        y = model.function(self.xdata, **coef)
        self.assertIsNotNone(y)

    def test_ssfpl(self):
        model = models.SSfpl()
        coef = model.fit(self.xdata, self.ydata)
        self.assertIsNotNone(coef)
        y = model.function(self.xdata, **coef)
        self.assertIsNotNone(y)

    def test_ssasymp(self):
        model = models.SSasymp()
        coef = model.fit(self.xdata, self.ydata)
        self.assertIsNotNone(coef)
        y = model.function(self.xdata, **coef)
        self.assertIsNotNone(y)


if __name__ == "__main__":
    unittest.main()
