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

from ohsome_quality_analyst.api import app

from .utils import api_schema_indicator, oqt_vcr


class TestApiIndicator(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Heidelberg
        self.dataset = "regions"
        self.feature_id = 3
        self.fid_field = "ogc_fid"

        # Heidelberg Altstadt
        # Choose a small enough region to not trigger area size limit
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

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
    def test_get_indicator_dataset_default_fid_field(self):
        url = "/indicator/{0}?layerName={1}&dataset={2}&featureId={3}".format(
            self.indicator_name, self.layer_name, self.dataset, self.feature_id
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    @oqt_vcr.use_cassette()
    def test_get_indicator_dataset_custom_fid_field(self):
        base_url = "/indicator/{0}?".format(self.indicator_name)
        parameter = "layerName={0}&dataset={1}&featureId={2}&fidField={3}".format(
            self.layer_name,
            self.dataset,
            self.feature_id,
            self.fid_field,
        )
        url = base_url + parameter
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    @oqt_vcr.use_cassette()
    def test_get_indicator_dataset_custom_fid_field_2(self):
        base_url = "/indicator/{0}?".format(self.indicator_name)
        parameter = "layerName={0}&dataset={1}&featureId={2}&fidField={3}".format(
            self.layer_name,
            self.dataset,
            "Heidelberg",
            "name",
        )
        url = base_url + parameter
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
    def test_post_indicator_dataset_default_fid_field(self):
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

    @oqt_vcr.use_cassette()
    def test_post_indicator_dataset_custom_fid_field(self):
        data = {
            "dataset": self.dataset,
            "featureId": self.feature_id,
            "layerName": self.layer_name,
            "fidField": self.fid_field,
        }
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))

    @oqt_vcr.use_cassette()
    def test_post_indicator_dataset_custom_fid_field_2(self):
        data = {
            "dataset": self.dataset,
            "featureId": "Heidelberg",
            "layerName": self.layer_name,
            "fidField": "name",
        }
        url = f"/indicator/{self.indicator_name}"
        response = self.client.post(url, json=data)

        self.assertEqual(response.status_code, 200)

        indicator = response.json()
        self.schema.validate(indicator)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(indicator))


if __name__ == "__main__":
    unittest.main()
