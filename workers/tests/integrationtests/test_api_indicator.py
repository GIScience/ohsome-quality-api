"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/

For tests regarding the `bpolys` parameter see `test_api_indicator_geojson_io.py`.
"""
import unittest
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app

from .api_response_schema import get_general_schema, get_indicator_feature_schema
from .utils import oqt_vcr

ENDPOINT = "/indicator"


class TestApiIndicator(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.indicator_name = "GhsPopComparisonBuildings"
        self.layer_name = "building_count"
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

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_default_fid_field(self):
        parameters = {
            "name": self.indicator_name,
            "layerName": self.layer_name,
            "dataset": self.dataset,
            "featureId": self.feature_id,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_custom_fid_field(self):
        parameters = {
            "name": self.indicator_name,
            "layerName": self.layer_name,
            "dataset": self.dataset,
            "featureId": self.feature_id,
            "fidField": self.fid_field,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_custom_fid_field_2(self):
        parameters = {
            "name": self.indicator_name,
            "layerName": self.layer_name,
            "dataset": self.dataset,
            "featureId": "Heidelberg",
            "fidField": "name",
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_invalid(self):
        parameters = {
            "name": self.indicator_name,
            "layerName": self.layer_name,
            "dataset": "foo",
            "featureId": self.feature_id,
        }
        response = self.client.post(ENDPOINT, json=parameters)
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_invalid_set_of_arguments(self):
        for parameters in (
            {
                "name": self.indicator_name,
                "layerName": "building_count",
                "dataset": "regions",
            },
            {
                "name": self.indicator_name,
                "layerName": "building_count",
                "feature_id": "3",
            },
        ):
            for response in (
                self.client.get(ENDPOINT + "?" + urlencode(parameters)),
                self.client.post(ENDPOINT, json=parameters),
            ):
                self.assertEqual(response.status_code, 422)
                content = response.json()
                self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_invalid_layer(self):
        parameters = {
            "name": self.indicator_name,
            "layerName": "amenities",
            "dataset": "regions",
            "featureId": "3",
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "RequestValidationError")


if __name__ == "__main__":
    unittest.main()
