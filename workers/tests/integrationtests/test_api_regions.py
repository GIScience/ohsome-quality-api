"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import unittest

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api import app


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_available_regions(self):
        url = "/regions"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(geojson.loads(response.content).is_valid)

    def test_get_list_indicators(self):
        url = "/list_indicators"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(geojson.loads(response.content).is_valid)


if __name__ == "__main__":
    unittest.main()
