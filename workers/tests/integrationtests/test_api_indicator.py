"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import os
import unittest
from typing import Optional

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app

from .api_response_schema import get_general_schema, get_indicator_feature_schema
from .utils import oqt_vcr


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
        if fid_field is not None:
            base_url = "/indicator/{0}?".format(self.indicator_name)
            parameter = "layerName={0}&dataset={1}&featureId={2}&fidField={3}".format(
                layer_name,
                dataset,
                feature_id,
                fid_field,
            )
            url = base_url + parameter
        else:
            url = "/indicator/{0}?layerName={1}&dataset={2}&featureId={3}".format(
                indicator_name,
                layer_name,
                dataset,
                feature_id,
            )
        return self.client.get(url)

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
                "dataset": self.dataset,
                "featureId": self.feature_id,
                "layerName": self.layer_name,
            }
        else:
            data = {
                "dataset": dataset,
                "featureId": feature_id,
                "layerName": layer_name,
                "fidField": fid_field,
            }
        url = "/indicator/{0}".format(indicator_name)
        return self.client.post(url, json=data)

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
            "dataset": "foo",
            "featureId": "3",
        }
        url = "/indicator/{0}".format(self.indicator_name)
        response = self.client.post(url, json=data)
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
        url = "/indicator/{0}".format(self.indicator_name)
        for data in (
            {
                "bpolys": bpolys,
                "dataset": "foo",
                "featureId": "3",
            },
            {"dataset": "regions"},
            {"feature_id": "3"},
        ):
            response = self.client.post(url, json=data)
            self.assertEqual(response.status_code, 422)

    @oqt_vcr.use_cassette()
    def test_indicator_include_svg(self):
        url = (
            "/indicator/{0}?layerName={1}&dataset={2}"
            "&featureId={3}&fidField={4}&includeSvg={5}".format(
                self.indicator_name,
                self.layer_name,
                self.dataset,
                self.feature_id,
                self.fid_field,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        self.assertIn("result.svg", list(result["properties"].keys()))

        url = (
            "/indicator/{0}?layerName={1}&dataset={2}"
            "&featureId={3}&fidField={4}&includeSvg={5}".format(
                self.indicator_name,
                self.layer_name,
                self.dataset,
                self.feature_id,
                self.fid_field,
                False,
            )
        )
        response = self.client.get(url)
        result = response.json()
        self.assertNotIn("result.svg", list(result["properties"].keys()))


if __name__ == "__main__":
    unittest.main()
