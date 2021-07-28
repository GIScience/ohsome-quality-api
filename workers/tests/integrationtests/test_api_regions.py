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
        url = "/list_regions"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(geojson.loads(response.content).is_valid)

    def test_get_list_indicators(self):
        url = "/list_indicators"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), list)
        self.assertIsNotNone(geojson.loads(response.content))

    def test_get_list_layers(self):
        url = "/list_layers"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), list)
        self.assertIsNotNone(geojson.loads(response.content))

    def test_get_list_datasets(self):
        url = "/list_datasets"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), list)
        self.assertIsNotNone(geojson.loads(response.content))

    def test_get_list_fid_field(self):
        url = "/list_fid_fields"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), list)
        self.assertIsNotNone(geojson.loads(response.content))

    def test_get_list_reports(self):
        url = "/list_reports"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(geojson.loads(response.content), list)
        self.assertIsNotNone(geojson.loads(response.content))


if __name__ == "__main__":
    unittest.main()
