import os
import unittest

import geojson

import ohsome_quality_analyst.utils.helper as helper


class TestHelper(unittest.TestCase):
    def setUp(self):
        pass

    def test_validate_geojson(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            hd_poly = geojson.load(f)

        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "europe.geojson",
        )
        with open(infile, "r") as f:
            europe_poly = geojson.load(f)

        self.assertTrue(helper.validate_geojson(hd_poly))
        self.assertRaises(ValueError, helper.validate_geojson, europe_poly)


if __name__ == "__main__":
    unittest.main()
