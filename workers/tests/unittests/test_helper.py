import os
import unittest

from geojson import Feature

from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport
from ohsome_quality_analyst.utils.definitions import load_metadata
from ohsome_quality_analyst.utils.helper import loads_geojson, name_to_class


def get_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return f.read()


class TestHelper(unittest.TestCase):
    def run_tests(self, raw: str, number_of_features: int = 1) -> None:
        i = 0
        for feature in loads_geojson(raw):
            i += 1
            self.assertIsInstance(feature, Feature)
        self.assertEqual(i, number_of_features)

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

    def test_loads_geojson_geometry(self):
        raw = get_fixture("heidelberg-altstadt-geometry.geojson")
        self.run_tests(raw)

    def test_loads_geojson_feature(self):
        raw = get_fixture("heidelberg-altstadt-feature.geojson")
        self.run_tests(raw)

    def test_loads_geojson_featurecollection(self):
        raw = get_fixture("featurecollection.geojson")
        self.run_tests(raw, number_of_features=2)

    def test_loads_geojson_featurecollection_single_feature(self):
        raw = get_fixture("heidelberg-altstadt-featurecollection.geojson")
        self.run_tests(raw)

    def test_loads_geojson_invalid_geojson(self):
        raw = get_fixture("ohsome-response-200-invalid.geojson")
        with self.assertRaises(ValueError):
            for _ in loads_geojson(raw):
                pass

    def test_loads_geojson_invalid_geometry_type(self):
        raw = get_fixture("line-string.geojson")
        with self.assertRaises(ValueError):
            for _ in loads_geojson(raw):
                pass


if __name__ == "__main__":
    unittest.main()
