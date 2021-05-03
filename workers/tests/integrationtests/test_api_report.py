"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
# API request tests are seperated for indicator and report
# because of a bug when using two schemata.


import os
import unittest

import geojson
from fastapi.testclient import TestClient
from schema import Optional, Or, Schema

from ohsome_quality_analyst.api import app
from ohsome_quality_analyst.reports.remote_mapping_level_one.report import (
    RemoteMappingLevelOne,
)

from .utils import oqt_vcr


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = "GhsPopComparisonBuildings"
        self.report_name = "SimpleReport"
        self.dataset = "regions"
        self.feature_id = 1
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

        self.schema = Schema(
            {
                "attribution": {
                    "url": str,
                    "text": str,
                },
                "apiVersion": str,
                "metadata": {
                    "name": str,
                    "description": str,
                    "requestUrl": str,
                },
                "result": {
                    "value": float,
                    "label": str,
                    "description": str,
                },
                "indicators": {
                    str: {
                        "metadata": {
                            "name": str,
                            "description": str,
                        },
                        "layer": {
                            "name": str,
                            "description": str,
                            "endpoint": str,
                            "filter": str,
                            Optional("ratio_filter"): Or(str, None),
                        },
                        "result": {
                            "timestamp_oqt": str,
                            "timestamp_osm": Or(str, None),
                            "value": float,
                            "label": str,
                            "description": str,
                            "svg": str,
                            Optional("data"): Or(dict, None),
                        },
                    }
                },
            }
        )

    @oqt_vcr.use_cassette()
    def test_get_report_dataset(self):
        url = "/report/{0}?dataset={1}&featureId={2}".format(
            self.report_name, self.dataset, self.feature_id
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
    def test_post_report_dataset(self):
        data = {"dataset": self.dataset, "featureId": self.feature_id}
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    @oqt_vcr.use_cassette()
    def test_number_of_indicator(self):
        data = {"dataset": self.dataset, "featureId": self.feature_id}
        url = "/report/RemoteMappingLevelOne"
        response = self.client.post(url, json=data)
        response_report = response.json()

        report = RemoteMappingLevelOne()
        report.set_indicator_layer()

        self.assertEqual(
            len(report.indicator_layer), len(response_report["indicators"].keys())
        )


if __name__ == "__main__":
    unittest.main()
