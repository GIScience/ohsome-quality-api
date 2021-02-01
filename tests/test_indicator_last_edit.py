import os
import unittest

import geojson

from ohsome_quality_tool.indicators.last_edit.indicator import LastEdit


class TestIndicatorLastEdit(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        self.indicator = LastEdit(bpolys=bpolys, layer_name="major_roads")

    def test(self):
        self.indicator.preprocess()

        self.indicator.calculate()
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)

        self.indicator.create_figure()


if __name__ == "__main__":
    unittest.main()
