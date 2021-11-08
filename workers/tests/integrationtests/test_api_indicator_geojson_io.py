"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import os
import unittest
from typing import Tuple
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app

from .api_response_schema import (
    get_featurecollection_schema,
    get_general_schema,
    get_indicator_feature_schema,
)
from .utils import get_geojson_fixture, oqt_vcr


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
        self.assertEqual(response.headers["content-type"], "application/geo+json")
        for schema in schemata:
            self.validate(response.json(), schema)

    def validate(self, geojson_: dict, schema: Schema) -> None:
        schema.validate(geojson_)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson_))

    def get_response(self, bpoly):
        """Return HTTP GET response"""
        parameters = urlencode(
            {
                "name": self.indicator_name,
                "layerName": self.layer_name,
                "bpolys": bpoly,
            }
        )
        return self.client.get("/indicator?" + parameters)

    def post_response(self, bpoly):
        """Return HTTP POST response"""
        parameters = {
            "name": self.indicator_name,
            "bpolys": bpoly,
            "layerName": self.layer_name,
        }
        return self.client.post("/indicator", json=parameters)

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_geometry(self):
        geometry = get_geojson_fixture("heidelberg-altstadt-geometry.geojson")
        for response in (self.get_response(geometry), self.post_response(geometry)):
            self.run_tests(response, (self.general_schema, self.feature_schema))

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_feature(self):
        feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        for response in (self.get_response(feature), self.post_response(feature)):
            self.run_tests(response, (self.general_schema, self.feature_schema))

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_featurecollection(self):
        featurecollection = get_geojson_fixture(
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
        feature = get_geojson_fixture("europe.geojson")
        for response in (
            self.get_response(feature),
            self.post_response(feature),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "SizeRestrictionError")

    @oqt_vcr.use_cassette()
    def test_invalid_set_of_arguments(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as f:
            bpolys = f.read()
        parameters = {
            "name": self.indicator_name,
            "bpolys": bpolys,
            "dataset": "foo",
            "featureId": "3",
        }

        for response in (
            self.client.get("/indicator?" + urlencode(parameters)),
            self.client.post("/indicator", json=parameters),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_include_svg(self):
        feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        url = "/indicator?name={0}&layerName={1}&bpolys={2}&includeSvg={3}".format(
            self.indicator_name,
            self.layer_name,
            feature,
            True,
        )
        response = self.client.get(url)
        result = response.json()
        self.assertIn("result.svg", list(result["properties"].keys()))

        url = "/indicator?name={0}&layerName={1}&bpolys={2}&includeSvg={3}".format(
            self.indicator_name,
            self.layer_name,
            feature,
            False,
        )
        response = self.client.get(url)
        result = response.json()
        self.assertNotIn("result.svg", list(result["properties"].keys()))

        url = "/indicator?name={0}&layerName={1}&bpolys={2}".format(
            self.indicator_name,
            self.layer_name,
            feature,
        )
        response = self.client.get(url)
        result = response.json()
        self.assertNotIn("result.svg", list(result["properties"].keys()))


if __name__ == "__main__":
    unittest.main()
