"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
# API request tests are seperated for indicator and report
# because of a bug when using two schemata.

import unittest
from typing import Optional

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api import app
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport

from .api_response_schema import get_feature_schema, get_response_schema
from .utils import oqt_vcr


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.report_name = "SimpleReport"
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = "3"
        self.fid_field = "ogc_fid"

        self.response_schema = get_response_schema()
        self.feature_schema = get_feature_schema()

        report = SimpleReport()
        report.set_indicator_layer()
        self.number_of_indicators = len(report.indicator_layer)

    def run_tests(self, response) -> None:
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.validate(response_json, self.response_schema)
        for i in range(0, self.number_of_indicators):
            feature_schema = get_feature_schema(i)
            self.validate(response_json, feature_schema)

    def validate(self, geojson: dict, schema: Schema) -> None:
        schema.validate(geojson)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson))

    def get_response(
        self,
        report_name: str,
        dataset: str,
        feature_id: str,
        fid_field: Optional[str] = None,
    ):
        """Return HTTP GET response"""
        if fid_field is not None:
            base_url = "/report/{0}?".format(self.report_name)
            parameter = "dataset={0}&featureId={1}&fidField={2}".format(
                dataset,
                feature_id,
                fid_field,
            )
            url = base_url + parameter
        else:
            url = "/report/{0}?dataset={1}&featureId={2}".format(
                report_name,
                dataset,
                feature_id,
            )
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
                "dataset": self.dataset,
                "featureId": self.feature_id,
            }
        else:
            data = {
                "dataset": dataset,
                "featureId": feature_id,
                "fidField": fid_field,
            }
        url = "/report/{0}".format(report_name)
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


if __name__ == "__main__":
    unittest.main()
