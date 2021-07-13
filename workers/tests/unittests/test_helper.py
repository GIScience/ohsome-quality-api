import os
import unittest

from geojson import Feature

from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport
from ohsome_quality_analyst.utils.definitions import load_metadata
from ohsome_quality_analyst.utils.helper import loads_geojson, name_to_class


class TestHelper(unittest.TestCase):
    def test_name_to_class(self):
        self.assertIs(
            name_to_class(class_type="indicator", name="GhsPopComparisonBuildings"),
            GhsPopComparisonBuildings,
        )

        self.assertIs(
            name_to_class(class_type="report", name="SimpleReport"),
            SimpleReport,
        )

        self.indicators = load_metadata("indicators")
        for indicator_name in self.indicators.keys():
            self.assertIsNotNone(
                name_to_class(class_type="indicator", name=indicator_name)
            )

    def test_loads_geojson(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "featurecollection.geojson",
        )
        with open(infile, "r") as file:
            raw = file.read()
        i = 0
        for feature in loads_geojson(raw):
            i += 1
            self.assertIsInstance(feature, Feature)
        self.assertEqual(i, 2)

        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-featurecollection.geojson",
        )
        with open(infile, "r") as file:
            raw = file.read()
        i = 0
        for feature in loads_geojson(raw):
            i += 1
            self.assertIsInstance(feature, Feature)
        self.assertEqual(i, 1)

        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(infile, "r") as file:
            raw = file.read()
        i = 0
        for feature in loads_geojson(raw):
            i += 1
            self.assertIsInstance(feature, Feature)
        self.assertEqual(i, 1)

        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )
        with open(infile, "r") as file:
            raw = file.read()
        i = 0
        for feature in loads_geojson(raw):
            i += 1
            self.assertIsInstance(feature, Feature)
        self.assertEqual(i, 1)

    def test_loads_geojson_invalid_geojson(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "ohsome-response-200-invalid.geojson",
        )
        with open(infile, "r") as file:
            raw = file.read()
        with self.assertRaises(ValueError):
            for _ in loads_geojson(raw):
                pass

    def test_loads_geojson_invalid_geometry_type(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "line-string.geojson",
        )
        with open(infile, "r") as file:
            raw = file.read()
        with self.assertRaises(ValueError):
            for _ in loads_geojson(raw):
                pass


if __name__ == "__main__":
    unittest.main()
