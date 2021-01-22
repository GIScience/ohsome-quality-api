import os
import unittest

import geojson

from ohsome_quality_tool import oqt


class TestOqt(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    def testCreateIndicator(self):
        self.assertIsNotNone(
            oqt.create_indicator("GhsPopComparison", "building_count", self.bpolys)
        )


if __name__ == "__main__":
    unittest.main()
