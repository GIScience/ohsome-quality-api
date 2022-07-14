import os
import unittest
from unittest import mock

import geojson

from ohsome_quality_analyst.indicators.minimal.indicator import Minimal


class TestGetDefaultFigure(unittest.TestCase):
    def test_get_default_figure(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)
        indicator = Minimal(feature=feature, layer=mock.Mock())
        self.assertIsInstance(indicator.result.svg, str)
        # TODO: Validate SVG
