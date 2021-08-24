"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import unittest

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_available_regions(self):
        url = "/regions"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(geojson.loads(response.content).is_valid)

    def test_get_list_indicators(self):
        url = "/indicatorNames"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), dict)

    def test_get_list_layers(self):
        url = "/layerNames"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), dict)

    def test_get_list_datasets(self):
        url = "/datasetNames"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), dict)

    def test_get_list_fid_field(self):
        url = "/FidFields"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), dict)

    def test_get_list_reports(self):
        url = "/reportNames"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), dict)


if __name__ == "__main__":
    unittest.main()
