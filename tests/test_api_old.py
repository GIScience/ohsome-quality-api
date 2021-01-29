import json
import os
import unittest

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_tool.api import app

# check out here for more info on fast api testing
# https://fastapi.tiangolo.com/tutorial/testing/
client = TestClient(app)


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.report_name = "SimpleReport"
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    def test_get_dynamic_report_api_request(self):
        """Test api response for dynamic report."""
        url = f"/dynamic/report/{self.report_name}?bpolys={self.bpolys}"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_dynamic_report_api_request(self):
        """Test api response for dynamic report."""
        data = {"bpolys": json.dumps(self.bpolys)}
        url = f"/dynamic/report/{self.report_name}"
        response = client.post(url, json=data)
        self.assertEqual(response.status_code, 200)

    def test_post_static_report_api_request(self):
        """Test api response for dynamic report."""
        data = {"dataset": "test_regions", "feature_id": 1}
        url = f"/static/report/{self.report_name}"
        response = client.post(url, json=data)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
