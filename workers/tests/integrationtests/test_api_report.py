"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/

For tests regarding the `bpolys` parameter see `test_api_report_geojson_io.py`.
"""
import unittest
from urllib.parse import urlencode

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport

from .api_response_schema import get_general_schema, get_report_feature_schema
from .utils import oqt_vcr

ENDPOINT = "/report"


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.report_name = "SimpleReport"
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = "3"
        self.fid_field = "ogc_fid"

        report = SimpleReport()
        report.set_indicator_layer()
        self.number_of_indicators = len(report.indicator_layer)

        self.general_schema = get_general_schema()
        self.feature_schema = get_report_feature_schema(self.number_of_indicators)

    def run_tests(self, response) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/geo+json")
        response_content = geojson.loads(response.content)
        self.assertTrue(response_content.is_valid)  # Valid GeoJSON?
        self.assertTrue(self.general_schema.is_valid(response_content))
        self.assertTrue(self.feature_schema.is_valid(response_content))

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_default_fid_field(self):
        parameters = {
            "name": self.report_name,
            "dataset": self.dataset,
            "featureId": self.feature_id,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_custom_fid_field(self):
        parameters = {
            "name": self.report_name,
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
    def test_get_report_dataset_custom_fid_field_2(self):
        parameters = {
            "name": self.report_name,
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
            "name": self.report_name,
            "dataset": "foo",
            "featureId": self.feature_id,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_invalid_set_of_arguments(self):
        for parameters in (
            {
                "name": self.report_name,
                "dataset": "regions",
            },
            {
                "name": self.report_name,
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


if __name__ == "__main__":
    unittest.main()
