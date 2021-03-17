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


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = "GhsPopComparison"
        self.report_name = "SimpleReport"
        self.dataset = "test_regions"
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
                            Optional("ratio_filter", default=None): Or(str, None),
                        },
                        "result": {
                            "value": float,
                            "label": str,
                            "description": str,
                            "svg": str,
                        },
                    }
                },
            }
        )

    # TODO: Mapping Saturation Error
    def test_get_report_dataset(self):
        url = "/report/{0}?dataset={1}&featureId={2}".format(
            self.report_name, self.dataset, self.feature_id
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    def test_post_report_bpolys(self):
        data = {"bpolys": geojson.dumps(self.bpolys)}
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))

    # TODO: Mapping Saturation Error
    def test_post_report_dataset(self):
        data = {"dataset": self.dataset, "featureId": self.feature_id}
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        report = response.json()
        self.schema.validate(report)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(report))


if __name__ == "__main__":
    unittest.main()
