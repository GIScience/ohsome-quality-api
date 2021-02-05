"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""


import os
import unittest

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_tool.api import app


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = "GhsPopComparison"
        self.report_name = "SimpleReport"
        self.layer_name = "building_count"
        self.dataset = "test_regions"
        self.feature_id = 1
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    def test_get_indicator_bpolys(self):
        url = "/indicator/{0}?layerName={1}&bpolys={2}".format(
            self.indicator_name,
            self.layer_name,
            self.bpolys,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_indicator_dataset(self):
        url = "/indicator/{0}?layerName={1}&dataset={2}&featureId={3}".format(
            self.indicator_name, self.layer_name, self.dataset, self.feature_id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_indicator_bpolys(self):
        data = {"bpolys": geojson.dumps(self.bpolys), "layerName": self.layer_name}
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)
        self.assertEqual(response.status_code, 200)

    def test_post_indicator_dataset(self):
        data = {
            "dataset": self.dataset,
            "featureId": self.feature_id,
            "layerName": self.layer_name,
        }
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)
        self.assertEqual(response.status_code, 200)

    def test_get_report_bpolys(self):
        url = "/report/{0}?bpolys={1}".format(self.report_name, self.bpolys)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_report_dataset(self):
        url = "/report/{0}?dataset={1}&featureId={2}".format(
            self.report_name, self.dataset, self.feature_id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_report_bpolys(self):
        data = {"bpolys": geojson.dumps(self.bpolys)}
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)
        self.assertEqual(response.status_code, 200)

    def test_post_report_dataset(self):
        data = {"dataset": self.dataset, "featureId": self.feature_id}
        url = f"/report/{self.report_name}"
        response = self.client.post(url, json=data)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
