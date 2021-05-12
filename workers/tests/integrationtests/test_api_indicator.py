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


class TestApiIndicator(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = "GhsPopComparisonBuildings"
        self.report_name = "SimpleReport"
        self.layer_name = "building_count"
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
                    "requestUrl": str,
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
        )

    def test_get_indicator_bpolys(self):
        url = "/indicator/{0}?layerName={1}&bpolys={2}".format(
            self.indicator_name,
            self.layer_name,
            self.bpolys,
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()

        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    def test_get_indicator_dataset(self):
        url = "/indicator/{0}?layerName={1}&dataset={2}&featureId={3}".format(
            self.indicator_name, self.layer_name, self.dataset, self.feature_id
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    def test_post_indicator_bpolys(self):
        data = {"bpolys": geojson.dumps(self.bpolys), "layerName": self.layer_name}
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    def test_post_indicator_dataset(self):
        data = {
            "dataset": self.dataset,
            "featureId": self.feature_id,
            "layerName": self.layer_name,
        }
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))


if __name__ == "__main__":
    unittest.main()
