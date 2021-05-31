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

from .utils import api_schema_indicator, oqt_vcr


class TestApiIndicator(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.dataset = "regions"
        self.feature_id = 1
        self.bpolys = asyncio.run(
            db_client.get_bpolys_from_db(self.dataset, self.feature_id, "ogc_fid")
        )
        self.indicator_name = "GhsPopComparisonBuildings"
        self.report_name = "SimpleReport"
        self.layer_name = "building_count"

        self.schema = api_schema_indicator

    @oqt_vcr.use_cassette()
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

    @oqt_vcr.use_cassette()
    def test_get_indicator_dataset(self):
        url = "/indicator/{0}?layerName={1}&dataset={2}&featureId={3}".format(
            self.indicator_name, self.layer_name, self.dataset, self.feature_id
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    @oqt_vcr.use_cassette()
    def test_post_indicator_bpolys(self):
        data = {"bpolys": geojson.dumps(self.bpolys), "layerName": self.layer_name}
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    @oqt_vcr.use_cassette()
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
