"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
# API request tests are seperated for indicator and report
# because of a bug when using two schemata.

import os
import unittest

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api import app
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport

from .api_response_schema import (
    get_feature_schema,
    get_featurecollection_schema,
    get_response_schema,
)
from .utils import oqt_vcr


def get_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return f.read()


class TestApiReportIo(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.report_name = "SimpleReport"
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = 3
        self.fid_field = "ogc_fid"

        self.response_schema = get_response_schema()
        self.feature_schema = get_feature_schema()
        self.featurecollection_schema = get_featurecollection_schema()

        report = SimpleReport()
        report.set_indicator_layer()
        self.number_of_indicators = len(report.indicator_layer)

    def run_tests(self, response, featurecollection=False) -> None:
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.validate(response, self.response_schema)
        if featurecollection is False:
            features = [response]
        else:
            features = response["features"]
        for feature in features:
            for i in range(0, self.number_of_indicators):
                feature_schema = get_feature_schema(i)
                self.validate(feature, feature_schema)

    def validate(self, geojson: dict, schema: Schema) -> None:
        schema.validate(geojson)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson))

    def get_response(self, bpoly):
        """Return HTTP GET response"""
        url = "/report/{0}?bpolys={1}".format(
            self.report_name,
            bpoly,
        )
        return self.client.get(url)

    def post_response(self, bpoly):
        """Return HTTP POST response"""
        url = "/report/{0}".format(self.report_name)
        return self.client.post(url, json={"bpolys": bpoly})

    @oqt_vcr.use_cassette()
    def test_report_bpolys_geometry(self):
        geometry = get_fixture("heidelberg-altstadt-geometry.geojson")
        for response in (self.get_response(geometry), self.post_response(geometry)):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_feature(self):
        feature = get_fixture("heidelberg-altstadt-feature.geojson")
        for response in (self.get_response(feature), self.post_response(feature)):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_featurecollection(self):
        featurecollection = get_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        for response in (
            self.get_response(featurecollection),
            self.post_response(featurecollection),
        ):
            self.run_tests(response, featurecollection=True)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_size_limit(self):
        feature = get_fixture("europe.geojson")
        with self.assertRaises(ValueError):
            self.get_response(feature)
        with self.assertRaises(ValueError):
            self.post_response(feature)


if __name__ == "__main__":
    unittest.main()
