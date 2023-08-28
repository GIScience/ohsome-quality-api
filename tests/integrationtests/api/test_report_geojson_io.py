"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/
"""
import unittest

from fastapi.testclient import TestClient
from geojson_pydantic import FeatureCollection

from ohsome_quality_analyst.api.api import app
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

        feature_collection = FeatureCollection(**response.content)  # Valid GeoJSON?
        self.assertTrue(self.general_schema.is_valid(feature_collection))
        self.assertTrue(self.feature_schema.is_valid(feature_collection))

    def post_response(self, bpoly):
        """Return HTTP POST response"""
        data = {"bpolys": bpoly}
        return self.client.post(self.endpoint, json=data)

    @oqt_vcr.use_cassette()
    def test_report_bpolys_featurecollection(self):
        response = self.post_response(self.featurecollection.model_dump())
        self.assertEqual(response.status_code, 200)

        FeatureCollection(**response.json())

        response_content = response.json()
        self.assertTrue(self.general_schema.is_valid(response_content))
        self.assertTrue(self.featurecollection_schema.is_valid(response_content))
        for feature in response_content["features"]:
            self.assertTrue(self.feature_schema.is_valid(feature))

    @oqt_vcr.use_cassette()
    def test_report_bpolys_size_limit(self):
        feature = get_geojson_fixture("europe.geojson")
        response = self.post_response(feature.model_dump())
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
