import unittest

import fixtures
import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation import models


class TestModels(unittest.TestCase):
    def test_sigmoid(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.Sigmoid()
        guess = model.initial_guess(xdata, ydata)
        self.assertTrue(guess)  # Not empty
        bounds = model.bounds(xdata, ydata)
        self.assertTrue(bounds)
        coef = model.fit(xdata, ydata)
        self.assertTrue(coef)
        ydata = model.function(xdata, **coef)
        self.assertTrue(np.any(ydata))

    def test_sigmoid_zero(self):
        ydata = fixtures.VALUES_ZERO
        xdata = np.asarray(range(len(ydata)))
        model = models.Sigmoid()
        guess = model.initial_guess(xdata, ydata)
        self.assertTrue(guess)  # Not empty
        bounds = model.bounds(xdata, ydata)
        self.assertTrue(bounds)
        coef = model.fit(xdata, ydata)
        self.assertTrue(coef)
        ydata = model.function(xdata, **coef)
        self.assertTrue(np.any(ydata))

    def test_sslogis(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSlogis()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_sslogis_zero(self):
        ydata = fixtures.VALUES_ZERO
        xdata = np.asarray(range(len(ydata)))
        model = models.SSlogis()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssdoubles(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSdoubleS()
        guess = model.initial_guess(xdata, ydata)
        self.assertIsNotNone(guess)
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssdoubles_zero(self):
        ydata = fixtures.VALUES_ZERO
        xdata = np.asarray(range(len(ydata)))
        model = models.SSdoubleS()
        guess = model.initial_guess(xdata, ydata)
        self.assertIsNotNone(guess)
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssfpl(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSfpl()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssfpl_zero(self):
        ydata = fixtures.VALUES_ZERO
        xdata = np.asarray(range(len(ydata)))
        model = models.SSfpl()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssasymp(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSasymp()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssasymp_zero(self):
        ydata = fixtures.VALUES_ZERO
        xdata = np.asarray(range(len(ydata)))
        model = models.SSasymp()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssmicmen(self):
        ydata = fixtures.VALUES
        xdata = np.asarray(range(len(ydata)))
        model = models.SSmicmen()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)

    def test_ssmicmen_zero(self):
        ydata = fixtures.VALUES_ZERO
        xdata = np.asarray(range(len(ydata)))
        model = models.SSmicmen()
        coef = model.fit(xdata, ydata)
        self.assertIsNotNone(coef)
        ydata = model.function(xdata, **coef)
        self.assertIsNotNone(ydata)


if __name__ == "__main__":
    unittest.main()
