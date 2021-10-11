"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import os
import unittest
import urllib.parse

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport

from .api_response_schema import (
    get_featurecollection_schema,
    get_general_schema,
    get_report_feature_schema,
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

        report = SimpleReport()
        report.set_indicator_layer()
        number_of_indicators = len(report.indicator_layer)

        self.general_schema = get_general_schema()
        self.feature_schema = get_report_feature_schema(number_of_indicators)
        self.featurecollection_schema = get_featurecollection_schema()

    def run_tests(self, response) -> None:
        self.assertEqual(response.status_code, 200)

        response_content = geojson.loads(response.content)
        self.assertTrue(response_content.is_valid)  # Valid GeoJSON?
        self.assertTrue(self.general_schema.is_valid(response_content))
        self.assertTrue(self.feature_schema.is_valid(response_content))

    def get_response(self, bpoly):
        """Return HTTP GET response"""
        parameters = urllib.parse.urlencode({"bpolys": bpoly})
        url = "/report/{0}?{1}".format(
            self.report_name,
            parameters,
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

            self.assertEqual(response.status_code, 200)

            response_geojson = geojson.loads(response.content)
            self.assertTrue(response_geojson.is_valid)  # Valid GeoJSON?

            response_content = response.json()
            self.assertTrue(self.general_schema.is_valid(response_content))
            self.assertTrue(self.featurecollection_schema.is_valid(response_content))
            for feature in response_content["features"]:
                self.assertTrue(self.feature_schema.is_valid(feature))

    @oqt_vcr.use_cassette()
    def test_report_bpolys_size_limit(self):
        feature = get_fixture("europe.geojson")
        with self.assertRaises(ValueError):
            self.get_response(feature)
        with self.assertRaises(ValueError):
            self.post_response(feature)

    @oqt_vcr.use_cassette()
    def test_report_include_svg(self):
        feature = get_fixture("heidelberg-altstadt-feature.geojson")
        url = "/report/{0}?bpolys={1}&include_svg={2}".format(
            self.report_name, feature, True
        )
        response = self.client.get(url)
        result = response.json()
        self.assertIn("indicators.0.result.svg", list(result["properties"].keys()))

        url = "/report/{0}?bpolys={1}&include_svg={2}".format(
            self.report_name, feature, False
        )
        response = self.client.get(url)
        result = response.json()
        self.assertNotIn("indicators.0.result.svg", list(result["properties"].keys()))


if __name__ == "__main__":
    unittest.main()
