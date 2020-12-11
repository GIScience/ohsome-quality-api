import json
import os
import unittest

from fastapi.testclient import TestClient

from ohsome_quality_tool.app.main import app

# check out here for more info on fast api testing
# https://fastapi.tiangolo.com/tutorial/testing/
client = TestClient(app)


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.report_name = "SIMPLE_REPORT"

    def test_get_dynamic_report_api_request(self):
        """Test api response for dynamic report."""
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile) as f:
            bpolys = json.dumps(json.load(f))

        url = f"http://127.0.0.1:8000/dynamic_report/{self.report_name}?bpolys={bpolys}"
        response = client.get(url)

        assert response.status_code == 200

    def test_post_dynamic_report_api_request(self):
        """Test api response for dynamic report."""
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile) as f:
            bpolys = json.dumps(json.load(f))

        data = {"bpolys": bpolys}

        url = f"http://127.0.0.1:8000/dynamic_report/{self.report_name}"
        response = client.post(url, json=data)

        assert response.status_code == 200


if __name__ == "__main__":
    unittest.main()
