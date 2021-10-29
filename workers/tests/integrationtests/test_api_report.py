"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import unittest
from typing import Optional
from urllib.parse import urlencode

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport

from .api_response_schema import get_general_schema, get_report_feature_schema
from .utils import oqt_vcr


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

    def get_response(
        self,
        report_name: str,
        dataset: str,
        feature_id: str,
        fid_field: Optional[str] = None,
    ):
        """Return HTTP GET response"""
        parameters_raw = {
            "name": report_name,
            "dataset": dataset,
            "featureId": feature_id,
        }
        base_url = "/report?"
        if fid_field is not None:
            parameters_raw["fidField"] = fid_field
        url = base_url + urlencode(parameters_raw)
        return self.client.get(url)

    def post_response(
        self,
        report_name: str,
        dataset: str,
        feature_id: str,
        fid_field: Optional[str] = None,
    ):
        """Return HTTP POST response"""
        if fid_field is not None:
            data = {
                "name": report_name,
                "dataset": dataset,
                "featureId": feature_id,
                "fidField": fid_field,
            }
        else:
            data = {
                "name": report_name,
                "dataset": dataset,
                "featureId": feature_id,
            }
        url = "/report"
        return self.client.post(url, json=data)

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_default_fid_field(self):
        parameters = (self.report_name, self.dataset, self.feature_id)
        for response in (
            self.get_response(*parameters),
            self.post_response(*parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_custom_fid_field(self):
        parameters = (self.report_name, self.dataset, self.feature_id, self.fid_field)
        for response in (
            self.get_response(*parameters),
            self.post_response(*parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_custom_fid_field_2(self):
        parameters = (self.report_name, self.dataset, "Heidelberg", "name")
        for response in (
            self.get_response(*parameters),
            self.post_response(*parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_report_include_svg(self):
        url = (
            "/report?name={0}&dataset={1}&featureId={2}&fidField={3}"
            "&includeSvg={4}".format(
                self.report_name,
                self.dataset,
                self.feature_id,
                self.fid_field,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        self.assertIn("indicators.0.result.svg", list(result["properties"].keys()))

        url = (
            "/report?name={0}&dataset={1}&featureId={2}&fidField={3}"
            "&includeSvg={4}".format(
                self.report_name,
                self.dataset,
                self.feature_id,
                self.fid_field,
                False,
            )
        )
        response = self.client.get(url)
        result = response.json()
        self.assertNotIn("indicators.0.result.svg", list(result["properties"].keys()))


if __name__ == "__main__":
    unittest.main()
