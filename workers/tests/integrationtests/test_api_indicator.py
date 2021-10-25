"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import os
import unittest
from typing import Optional
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

    def get_response(
        self,
        indicator_name: str,
        layer_name: str,
        dataset: str,
        feature_id: str,
        fid_field: Optional[str] = None,
    ):
        """Return HTTP GET response"""
        parameters_raw = {
            "name": indicator_name,
            "layerName": layer_name,
            "dataset": dataset,
            "featureId": feature_id,
        }
        if fid_field is not None:
            parameters_raw["fidField"] = fid_field
        return self.client.get(ENDPOINT + "?" + urlencode(parameters_raw))

    def post_response(
        self,
        indicator_name: str,
        layer_name: str,
        dataset: str,
        feature_id: str,
        fid_field: Optional[str] = None,
    ):
        """Return HTTP POST response"""
        if fid_field is not None:
            data = {
                "name": indicator_name,
                "dataset": dataset,
                "layerName": layer_name,
                "featureId": feature_id,
                "fidField": fid_field,
            }
        else:
            data = {
                "name": indicator_name,
                "dataset": dataset,
                "layerName": layer_name,
                "featureId": feature_id,
            }
        return self.client.post(ENDPOINT, json=data)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_default_fid_field(self):
        parameters = (
            self.indicator_name,
            self.layer_name,
            self.dataset,
            self.feature_id,
        )
        for response in (
            self.get_response(*parameters),
            self.post_response(*parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_custom_fid_field(self):
        parameters = (
            self.indicator_name,
            self.layer_name,
            self.dataset,
            self.feature_id,
            self.fid_field,
        )
        for response in (
            self.get_response(*parameters),
            self.post_response(*parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_custom_fid_field_2(self):
        parameters = (
            self.indicator_name,
            self.layer_name,
            self.dataset,
            "Heidelberg",
            "name",
        )
        for response in (
            self.get_response(*parameters),
            self.post_response(*parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_invalid(self):
        data = {
            "name": self.indicator_name,
            "layerName": self.layer_name,
            "dataset": "foo",
            "featureId": "3",
        }
        response = self.client.post(ENDPOINT, json=data)
        self.assertEqual(response.status_code, 422)

    @oqt_vcr.use_cassette()
    def test_indicator_invalid_set_of_arguments(self):

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as f:
            bpolys = f.read()
        for data in (
            {
                "name": self.indicator_name,
                "bpolys": bpolys,
                "dataset": "foo",
                "featureId": "3",
            },
            {
                "name": self.indicator_name,
                "dataset": "regions",
            },
            {"name": self.indicator_name, "feature_id": "3"},
        ):
            response = self.client.post(ENDPOINT, json=data)
            self.assertEqual(response.status_code, 422)

    @oqt_vcr.use_cassette()
    def test_indicator_invalid_layer(self):
        data = {
            "name": self.indicator_name,
            "layerName": "amenities",
            "dataset": "foo",
            "featureId": "3",
        }
        response = self.client.post(ENDPOINT, json=data)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
