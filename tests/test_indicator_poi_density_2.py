import os
import unittest

import geojson

from ohsome_quality_tool.indicators.poi_density.indicator import PoiDensity


class TestIndicatorPoiDensity(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        self.indicator = PoiDensity(dynamic=True, bpolys=bpolys, layer_name="poi")

    def test(self):
        self.indicator.preprocess()
        self.assertIsNotNone(self.indicator.area_sqkm)
        self.assertIsNotNone(self.indicator.count)
        self.assertIsNotNone(self.indicator.density)

        self.indicator.calculate()
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)

        self.indicator.create_figure()


if __name__ == "__main__":
    unittest.main()
