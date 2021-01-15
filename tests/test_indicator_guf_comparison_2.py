import os
import unittest

import geojson

from ohsome_quality_tool.indicators.guf_comparison.indicator import GufComparison


class TestIndicatorGufComparison(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        self.indicator = GufComparison(dynamic=True, bpolys=bpolys)

    def test_preprocess(self):
        self.indicator.preprocess()

    def test_calculate(self):
        pass

    def test_create_figure(self):
        pass


if __name__ == "__main__":
    unittest.main()
