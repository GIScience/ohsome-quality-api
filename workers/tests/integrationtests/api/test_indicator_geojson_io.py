"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import os
import unittest
from datetime import datetime, timedelta
from typing import Tuple

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app
from tests.integrationtests.api.response_schema import (
    get_featurecollection_schema,
    get_general_schema,
    get_indicator_feature_schema,
)
from tests.integrationtests.utils import get_geojson_fixture, oqt_vcr
from tests.unittests.mapping_saturation.fixtures import VALUES_1 as DATA

HEADERS = {"accept": "application/geo+json"}


class TestApiIndicatorIo(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.endpoint = "/indicators/minimal"
        self.topic_key = "minimal"
        self.feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        self.feature_schema = get_indicator_feature_schema()
        self.general_schema = get_general_schema()
        self.featurecollection_schema = get_featurecollection_schema()

    def run_tests(self, response, schemata: Tuple[Schema]) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/geo+json")
        for schema in schemata:
            self.validate(response.json(), schema)

    def validate(self, geojson_: dict, schema: Schema) -> None:
        schema.validate(geojson_)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson_))

    def post_response(self, bpoly):
        """Return HTTP POST response"""
        parameters = {
            "bpolys": bpoly,
            "topic": self.topic_key,
        }
        return self.client.post(self.endpoint, json=parameters, headers=HEADERS)

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_feature(self):
        response = self.post_response(self.feature)
        self.run_tests(response, (self.general_schema, self.featurecollection_schema))

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_featurecollection(self):
        featurecollection = get_geojson_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson"
        )
        response = self.post_response(featurecollection)
        self.run_tests(response, (self.general_schema, self.featurecollection_schema))
        for feature in response.json()["features"]:
            self.assertIn("id", feature.keys())
            self.validate(feature, self.feature_schema)

    @oqt_vcr.use_cassette()
    def test_indicator_bpolys_size_limit(self):
        feature = get_geojson_fixture("europe.geojson")
        response = self.post_response(feature)
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "SizeRestrictionError")

    @oqt_vcr.use_cassette()
    def test_invalid_set_of_arguments(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as f:
            bpolys = f.read()
        parameters = {
            "bpolys": bpolys,
            "dataset": "foo",
            "feature_id": "3",
        }
        response = self.client.post(self.endpoint, json=parameters)
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_include_svg(self):
        feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        parameters = {
            "topic": self.topic_key,
            "bpolys": feature,
            "includeSvg": True,
        }
        response = self.client.post(self.endpoint, json=parameters, headers=HEADERS)
        result = response.json()
        for feat in result["features"]:
            assert "svg" in feat["properties"]["result"]

        parameters = {
            "topic": self.topic_key,
            "bpolys": feature,
            "includeSvg": False,
        }
        response = self.client.post(self.endpoint, json=parameters, headers=HEADERS)
        result = response.json()
        for feat in result["features"]:
            assert "svg" not in feat["properties"]["result"]

        parameters = {
            "topic": self.topic_key,
            "bpolys": feature,
        }
        response = self.client.post(self.endpoint, json=parameters, headers=HEADERS)
        result = response.json()
        for feat in result["features"]:
            self.assertNotIn("result.svg", list(feat["properties"].keys()))

    @oqt_vcr.use_cassette()
    def test_indicator_include_html(self):
        feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        parameters = {
            "topic": self.topic_key,
            "bpolys": feature,
            "includeSvg": True,
            "includeHtml": True,
        }
        response = self.client.post(self.endpoint, json=parameters, headers=HEADERS)
        result = response.json()
        for feat in result["features"]:
            assert "html" in feat["properties"]["result"]

        parameters = {
            "topic": self.topic_key,
            "bpolys": feature,
            "includeSvg": False,
            "includeHtml": False,
        }
        response = self.client.post(self.endpoint, json=parameters, headers=HEADERS)
        result = response.json()
        for feat in result["features"]:
            assert "html" not in feat["properties"]["result"]

        parameters = {
            "topic": self.topic_key,
            "bpolys": feature,
        }
        response = self.client.post(self.endpoint, json=parameters, headers=HEADERS)
        result = response.json()
        for feat in result["features"]:
            assert "html" not in feat["properties"]["result"]

    def test_indicator_topic_data(self):
        """Test parameter Topic with data attached.

        Data are the ohsome API response result values for Heidelberg and the topic
        `building-count`.
        """
        timestamp_objects = [
            datetime(2020, 7, 17, 9, 10, 0) + timedelta(days=1 * x)
            for x in range(DATA.size)
        ]
        timestamp_iso_string = [
            t.strftime("%Y-%m-%dT%H:%M:%S") for t in timestamp_objects
        ]

        parameters = {
            "bpolys": self.feature,
            "topic": {
                "key": "foo",
                "name": "bar",
                "description": "",
                "data": {
                    "result": [
                        {"value": v, "timestamp": t}
                        for v, t in zip(DATA, timestamp_iso_string)
                    ]
                },
            },
        }
        response = self.client.post(
            "/indicators/mapping-saturation", json=parameters, headers=HEADERS
        )
        self.run_tests(response, (self.general_schema, self.featurecollection_schema))

    def test_indicator_topic_data_invalid(self):
        parameters = {
            "bpolys": self.feature,
            "topic": {
                "key": "foo",
                "name": "bar",
                "description": "",
                "data": {"result": [{"value": 1.0}]},  # Missing timestamp item
            },
        }
        response = self.client.post(
            "/indicators/mapping-saturation", json=parameters, headers=HEADERS
        )
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "TopicDataSchemaError")


if __name__ == "__main__":
    unittest.main()
