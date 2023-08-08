"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import unittest

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app
from ohsome_quality_analyst.utils.validators import InvalidCRSError, validate_geojson
from tests.integrationtests.api.response_schema import (
    get_featurecollection_schema,
    get_general_schema,
    get_report_feature_schema,
)
from tests.integrationtests.utils import get_geojson_fixture, oqt_vcr
from tests.utils import load_geojson_fixture


class TestApiReportIo(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.endpoint = "/reports/minimal"

        self.featurecollection = load_geojson_fixture(
            "feature-collection-germany-heidelberg.geojson"
        )

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
        data = {"bpolys": bpoly}
        return self.client.post(self.endpoint, json=data)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_featurecollection(self):
        response = self.post_response(self.featurecollection)
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
    def test_wrong_crs(self):
        feature = get_geojson_fixture("heidelberg-altstadt-epsg32632.geojson")

        with self.assertRaises(InvalidCRSError) as context:
            validate_geojson(feature)
        exception = context.exception
        self.assertEqual(exception.error_code, 400)
        self.assertEqual(
            exception.args[0],
            "Invalid CRS. The FeatureCollection must have the EPSG:4326 CRS or none.",
        )


if __name__ == "__main__":
    unittest.main()
