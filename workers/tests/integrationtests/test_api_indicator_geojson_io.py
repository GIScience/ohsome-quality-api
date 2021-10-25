"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import os
import unittest
from typing import Tuple
from unittest import mock
from unittest.mock import MagicMock
from urllib.parse import urlencode

import geojson
import httpx
from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app

from .api_response_schema import (
    get_featurecollection_schema,
    get_general_schema,
    get_indicator_feature_schema,
)
from .utils import oqt_vcr


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def get_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


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

    def validate(self, geojson: dict, schema: Schema) -> None:
        schema.validate(geojson)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson))

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
        for response in (
            self.get_response(feature),
            self.post_response(feature),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "SizeRestrictionError")

    @oqt_vcr.use_cassette()
    def test_bpolys_invalid(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "invalid.geojson",
        )
        with open(path, "r") as file:
            bpolys = file.read()
        for response in (
            self.get_response(bpolys),
            self.post_response(bpolys),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "RequestValidationError")

    def test_ohsome_timeout(self):
        invalid_response = get_fixture("ohsome-response-200-invalid.geojson")
        featurecollection = get_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        with mock.patch(
            "httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=invalid_response,
                request=httpx.Request("POST", "https://www.example.org/"),
            )

            for response in (
                self.get_response(featurecollection),
                self.post_response(featurecollection),
            ):
                self.assertEqual(response.status_code, 422)
                content = response.json()
                self.assertEqual(content["type"], "OhsomeApiError")

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

        response = self.client.get("/indicator?" + urlencode(parameters))
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "RequestValidationError")

        response = self.client.post("/indicator", json=parameters)
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "RequestValidationError")


if __name__ == "__main__":
    unittest.main()
