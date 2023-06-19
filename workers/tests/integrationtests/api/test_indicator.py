"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/

For tests regarding the `bpolys` parameter see `test_api_indicator_geojson_io.py`.
"""
import unittest

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app
from tests.integrationtests.api.response_schema import (
    get_general_schema,
    get_indicator_feature_schema,
)
from tests.integrationtests.utils import oqt_vcr

ENDPOINT = "/indicators/minimal"


class TestApiIndicator(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.topic_key = "minimal"
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = "3"
        self.fid_field = "ogc_fid"

        self.general_schema = get_general_schema()
        self.feature_schema = get_indicator_feature_schema()

    def run_tests(self, response) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/geo+json")
        for schema in (self.general_schema, self.feature_schema):
            self.validate(response.json(), schema)

    def validate(self, geojson: dict, schema: Schema) -> None:
        schema.validate(geojson)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson))

    @oqt_vcr.use_cassette
    def test_indicator_dataset_default_fid_field(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature_id": self.feature_id,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        self.run_tests(response)

    @oqt_vcr.use_cassette
    def test_indicator_dataset_custom_fid_field(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature_id": self.feature_id,
            "fid_field": self.fid_field,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        self.run_tests(response)

    @oqt_vcr.use_cassette
    def test_indicator_dataset_custom_fid_field_2(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature_id": "Heidelberg",
            "fid_field": "name",
        }
        response = self.client.post(ENDPOINT, json=parameters)
        self.run_tests(response)

    @oqt_vcr.use_cassette
    def test_indicator_dataset_invalid(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": "foo",
            "feature_id": self.feature_id,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette
    def test_indicator_invalid_set_of_arguments(self):
        for parameters in (
            {
                "topic": "building_count",
                "dataset": "regions",
            },
            {
                "topic": "building_count",
                "feature_id": "3",
            },
        ):
            response = self.client.post(ENDPOINT, json=parameters)
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette
    def test_indicator_include_svg_true(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "include-svg": True,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "svg" in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_include_svg_false(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "include-svg": False,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "svg" not in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_include_svg_default(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "svg" not in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_invalid_topic(self):
        parameters = {
            "topic": "amenities",
            "dataset": "regions",
            "feature_id": "3",
        }
        response = self.client.post(ENDPOINT, json=parameters)
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette
    def test_indicator_include_html_true(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "include-html": True,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "html" in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_include_html_false(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "include-html": False,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "html" not in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_include_html_default(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "html" not in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_flatten_default(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        # Check flat result value
        assert "result.value" not in result["properties"]
        assert "value" in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_flatten_true(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "flatten": True,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "result.value" in result["properties"]

    @oqt_vcr.use_cassette
    def test_indicator_flatten_false(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "flatten": False,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "result.value" not in result["properties"]
        assert "value" in result["properties"]["result"]

    @oqt_vcr.use_cassette
    def test_indicator_include_data_default(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "data" not in result["properties"]

    @oqt_vcr.use_cassette
    def test_indicator_include_data_true(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "include-data": True,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "data" in result["properties"]

    @oqt_vcr.use_cassette
    def test_indicator_include_data_false(self):
        parameters = {
            "topic": self.topic_key,
            "dataset": self.dataset,
            "feature-id": self.feature_id,
            "include-data": False,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        result = response.json()
        assert "data" not in result["properties"]


if __name__ == "__main__":
    unittest.main()
