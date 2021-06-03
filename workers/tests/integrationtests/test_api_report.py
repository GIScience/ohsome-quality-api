"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
# API request tests are seperated for indicator and report
# because of a bug when using two schemata.


import asyncio
import unittest

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api import app
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport

from .utils import api_schema_report, oqt_vcr


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.dataset = "regions"
        self.feature_id = 31
        self.bpolys = asyncio.run(
            db_client.get_bpolys_from_db(self.dataset, self.feature_id, "ogc_fid")
        )
        self.report_name = "SimpleReport"

        self.schema = api_schema_report

    @oqt_vcr.use_cassette()
    def test_get_report_bpolys(self):
        url = "/report/{0}?bpolys={1}".format(self.report_name, self.bpolys)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_default_fid_field(self):
        url = "/report/{0}?dataset={1}&featureId={2}".format(
            self.report_name, self.dataset, self.feature_id
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_custom_fid_field(self):
        url = "/report/{0}?dataset={1}&featureId={2}&fidField={3}".format(
            self.report_name, self.dataset, self.feature_id, "ogc_fid"
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_custom_fid_field_2(self):
        url = "/report/{0}?dataset={1}&featureId={2}&fidField={3}".format(
            self.report_name, self.dataset, "Alger Kenadsa medium", "name"
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_post_report_bpolys(self):
        data = {"bpolys": geojson.dumps(self.bpolys)}
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_post_report_dataset_default_fid_field(self):
        data = {"dataset": self.dataset, "featureId": self.feature_id}
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_post_report_dataset_custom_fid_field(self):
        data = {
            "dataset": self.dataset,
            "featureId": self.feature_id,
            "fidField": "ogc_fid",
        }
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_post_report_dataset_custom_fid_field_2(self):
        data = {
            "dataset": self.dataset,
            "featureId": self.feature_id,
            "Alger Kenadsa medium": "name",
        }
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_number_of_indicator(self):
        data = {"dataset": self.dataset, "featureId": self.feature_id}
        url = "/report/{0}".format(self.report_name)
        response = self.client.post(url, json=data)
        response_report = response.json()

        report = SimpleReport()
        report.set_indicator_layer()

        self.assertEqual(
            len(report.indicator_layer), len(response_report["indicators"].keys())
        )


if __name__ == "__main__":
    unittest.main()
