"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import os
import unittest
from typing import Tuple

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app

from .api_response_schema import (
    get_featurecollection_schema,
    get_general_schema,
    get_indicator_feature_schema,
)
from .utils import oqt_vcr


def get_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return f.read()


class TestApiIndicatorIo(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.indicator_name = "GhsPopComparisonBuildings"
        self.layer_name = "building_count"

        self.general_schema = get_general_schema()
        self.feature_schema = get_indicator_feature_schema()
        self.featurecollection_schema = get_featurecollection_schema()

    def run_tests(self, response, schemata: Tuple[Schema]) -> None:
        self.assertEqual(response.status_code, 200)
        for schema in schemata:
            self.validate(response.json(), schema)

    def validate(self, geojson: dict, schema: Schema) -> None:
        schema.validate(geojson)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson))

    def get_response(self, bpoly):
        """Return HTTP GET response"""
        url = "/indicator/{0}?layerName={1}&bpolys={2}".format(
            self.indicator_name,
            self.layer_name,
            bpoly,
        )
        return self.client.get(url)

    def post_response(self, bpoly):
        """Return HTTP POST response"""
        data = {"bpolys": bpoly, "layerName": self.layer_name}
        url = f"/indicator/{self.indicator_name}"
        return self.client.post(url, json=data)

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_geometry(self):
        geometry = get_fixture("heidelberg-altstadt-geometry.geojson")
        for response in (self.get_response(geometry), self.post_response(geometry)):
            self.run_tests(response, (self.general_schema, self.feature_schema))

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_feature(self):
        feature = get_fixture("heidelberg-altstadt-feature.geojson")
        for response in (self.get_response(feature), self.post_response(feature)):
            self.run_tests(response, (self.general_schema, self.feature_schema))

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_featurecollection(self):
        featurecollection = get_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        for response in (
            self.get_response(featurecollection),
            self.post_response(featurecollection),
        ):
            self.run_tests(
                response, (self.general_schema, self.featurecollection_schema)
            )
            for feature in response.json()["features"]:
                self.assertIn("id", feature.keys())
                self.validate(feature, self.feature_schema)

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_size_limit(self):
        feature = get_fixture("europe.geojson")
        with self.assertRaises(ValueError):
            self.get_response(feature)
        with self.assertRaises(ValueError):
            self.post_response(feature)

    @oqt_vcr.use_cassette()
    def test_bpolys_invalid(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "invalid.geojson",
        )
        with open(path, "r") as file:
            bpolys = file.read()
        data = {"bpolys": bpolys, "layerName": self.layer_name}
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)
        self.assertEqual(response.status_code, 422)

    @oqt_vcr.use_cassette()
    def test_indicator_include_svg(self):
        feature = get_fixture("heidelberg-altstadt-feature.geojson")
        url = "/indicator/{0}?layerName={1}&bpolys={2}&include_svg={3}".format(
            self.indicator_name,
            self.layer_name,
            feature,
            True,
        )
        response = self.client.get(url)
        result = response.json()
        self.assertIn("result.svg", list(result["properties"].keys()))

        url = "/indicator/{0}?layerName={1}&bpolys={2}&include_svg={3}".format(
            self.indicator_name,
            self.layer_name,
            feature,
            False,
        )
        response = self.client.get(url)
        result = response.json()
        self.assertNotIn("result.svg", list(result["properties"].keys()))


if __name__ == "__main__":
    unittest.main()
