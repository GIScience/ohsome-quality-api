import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.indicators.ghs_pop_comparison.indicator import (
    GhsPopComparison,
)


class TestIndicatorGhsPopComparison(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        self.indicator = GhsPopComparison(bpolys=bpolys, layer_name="building_count")

    def test(self):
        asyncio.run(self.indicator.preprocess())
        self.assertIsNotNone(self.indicator.pop_count)
        self.assertIsNotNone(self.indicator.area)
        self.assertIsNotNone(self.indicator.feature_count)
        self.assertIsNotNone(self.indicator.feature_count_per_sqkm)
        self.assertIsNotNone(self.indicator.pop_count_per_sqkm)

        self.indicator.calculate()
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)

        self.indicator.create_figure()
        self.assertIsNotNone(self.indicator.result.svg)


if __name__ == "__main__":
    unittest.main()
