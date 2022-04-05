"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import unittest

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app

from .api_response_schema import (
    get_featurecollection_schema,
    get_general_schema,
    get_report_feature_schema,
)
from .utils import get_geojson_fixture, oqt_vcr


class TestApiReportIo(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.endpoint = "/report"

        self.report_name = "SimpleReport"
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = 3
        self.fid_field = "ogc_fid"

        number_of_indicators = 2

        self.general_schema = get_general_schema()
        self.feature_schema = get_report_feature_schema(number_of_indicators)
        self.featurecollection_schema = get_featurecollection_schema()

    def run_tests(self, response) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/geo+json")

        response_content = geojson.loads(response.content)
        self.assertTrue(response_content.is_valid)  # Valid GeoJSON?
        self.assertTrue(self.general_schema.is_valid(response_content))
        self.assertTrue(self.feature_schema.is_valid(response_content))

    def post_response(self, bpoly):
        """Return HTTP POST response"""
        data = {"name": self.report_name, "bpolys": bpoly}
        return self.client.post(self.endpoint, json=data)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_geometry(self):
        geometry = get_geojson_fixture("heidelberg-altstadt-geometry.geojson")
        response = self.post_response(geometry)
        self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_feature(self):
        feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        response = self.post_response(feature)
        self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_featurecollection(self):
        featurecollection = get_geojson_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        response = self.post_response(featurecollection)
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
        feature = get_geojson_fixture("europe.geojson")
        response = self.post_response(feature)
        self.assertEqual(response.status_code, 422)

    @oqt_vcr.use_cassette()
    def test_invalid_set_of_arguments(self):
        bpolys = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        parameters = {
            "name": self.report_name,
            "bpolys": bpolys,
            "dataset": "foo",
            "featureId": "3",
        }
        response = self.client.post(self.endpoint, json=parameters)
        self.assertEqual(response.status_code, 422)
        content = response.json()
        self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_report_include_svg(self):
        feature = get_geojson_fixture("niger-kanan-bakache.geojson")
        parameters = {
            "name": self.report_name,
            "bpolys": feature,
            "includeSvg": True,
        }
        response = self.client.post(self.endpoint, json=parameters)
        result = response.json()
        self.assertIn("indicators.0.result.svg", list(result["properties"].keys()))

        parameters = {
            "name": self.report_name,
            "bpolys": feature,
            "includeSvg": False,
        }
        response = self.client.post(self.endpoint, json=parameters)
        result = response.json()
        self.assertNotIn("indicators.0.result.svg", list(result["properties"].keys()))

        parameters = {
            "name": self.report_name,
            "bpolys": feature,
        }
        response = self.client.post(self.endpoint, json=parameters)
        result = response.json()
        self.assertNotIn("indicators.0.result.svg", list(result["properties"].keys()))

    @oqt_vcr.use_cassette()
    def test_report_include_html(self):
        feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        parameters = {
            "name": self.report_name,
            "bpolys": feature,
            "includeSvg": False,
            "includeHtml": True,
        }
        response = self.client.post(self.endpoint, json=parameters)
        result = response.json()
        self.assertIn("report.result.html", list(result["properties"].keys()))
        parameters = {
            "name": self.report_name,
            "bpolys": feature,
            "includeSvg": False,
            "includeHtml": False,
        }
        response = self.client.post(self.endpoint, json=parameters)
        result = response.json()
        self.assertNotIn("report.result.html", list(result["properties"].keys()))

        parameters = {
            "name": self.report_name,
            "bpolys": feature,
        }
        response = self.client.post(self.endpoint, json=parameters)
        result = response.json()
        self.assertNotIn("report.result.html", list(result["properties"].keys()))


if __name__ == "__main__":
    unittest.main()
