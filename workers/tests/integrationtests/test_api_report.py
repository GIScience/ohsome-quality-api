"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/

For tests regarding the `bpolys` parameter see `test_api_report_geojson_io.py`.
"""
import unittest
from urllib.parse import urlencode

import geojson
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app

from .api_response_schema import get_general_schema, get_report_feature_schema
from .utils import oqt_vcr

ENDPOINT = "/report"


class TestApiReport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.report_name = "MinimalTestReport"
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = "3"
        self.fid_field = "ogc_fid"

        self.number_of_indicators = 2

        self.general_schema = get_general_schema()
        self.feature_schema = get_report_feature_schema(self.number_of_indicators)

    def run_tests(self, response) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/geo+json")
        response_content = geojson.loads(response.content)
        self.general_schema.validate(response_content)
        self.feature_schema.validate(response_content)
        self.assertTrue(response_content.is_valid)  # Valid GeoJSON?
        self.assertTrue(self.general_schema.is_valid(response_content))
        self.assertTrue(self.feature_schema.is_valid(response_content))

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_default_fid_field(self):
        parameters = {
            "name": self.report_name,
            "dataset": self.dataset,
            "featureId": self.feature_id,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_custom_fid_field(self):
        parameters = {
            "name": self.report_name,
            "dataset": self.dataset,
            "featureId": self.feature_id,
            "fidField": self.fid_field,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_get_report_dataset_custom_fid_field_2(self):
        parameters = {
            "name": self.report_name,
            "dataset": self.dataset,
            "featureId": "Heidelberg",
            "fidField": "name",
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_report_include_svg_true(self):
        url = (
            "/report?name={0}&dataset={1}&featureId={2}&fidField={3}"
            "&includeSvg={4}".format(
                self.report_name,
                self.dataset,
                self.feature_id,
                self.fid_field,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "svg" in result["properties"]["indicators"][0]["result"]

    def test_report_include_svg_false(self):
        url = (
            "/report?name={0}&dataset={1}&featureId={2}&fidField={3}"
            "&includeSvg={4}".format(
                self.report_name,
                self.dataset,
                self.feature_id,
                self.fid_field,
                False,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "svg" not in result["properties"]["indicators"][0]["result"]

    def test_report_include_svg_default(self):
        url = "/report?name={0}&dataset={1}&featureId={2}&fidField={3}".format(
            self.report_name,
            self.dataset,
            self.feature_id,
            self.fid_field,
        )
        response = self.client.get(url)
        result = response.json()
        assert "svg" not in result["properties"]["indicators"][0]["result"]

    def test_indicator_dataset_invalid(self):
        parameters = {
            "name": self.report_name,
            "dataset": "foo",
            "featureId": self.feature_id,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_invalid_set_of_arguments(self):
        for parameters in (
            {
                "name": self.report_name,
                "dataset": "regions",
            },
            {
                "name": self.report_name,
                "feature_id": "3",
            },
        ):
            for response in (
                self.client.get(ENDPOINT + "?" + urlencode(parameters)),
                self.client.post(ENDPOINT, json=parameters),
            ):
                self.assertEqual(response.status_code, 422)
                content = response.json()
                self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_include_html(self):
        url = (
            "/report?name={0}&dataset={1}&featureId={2}&fidField={3}"
            "&includeHtml={4}".format(
                self.report_name,
                self.dataset,
                self.feature_id,
                self.fid_field,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "html" in result["properties"]["report"]["result"]

    @oqt_vcr.use_cassette()
    def test_report_flatten_default(self):
        url = "/report?name={0}&dataset={1}&featureId={2}".format(
            self.report_name,
            self.dataset,
            self.feature_id,
        )
        response = self.client.get(url)
        result = response.json()
        # Check flat result value
        assert "report.result.value" not in result["properties"]
        assert "value" in result["properties"]["report"]["result"]
        assert "indicators.0.result.value" not in result["properties"]
        assert "value" in result["properties"]["indicators"][0]["result"]

    @oqt_vcr.use_cassette()
    def test_report_flatten_true(self):
        url = "/report?name={0}&dataset={1}&featureId={2}&flatten={3}".format(
            self.report_name,
            self.dataset,
            self.feature_id,
            True,
        )
        response = self.client.get(url)
        result = response.json()
        assert "report.result.value" in result["properties"]
        assert "indicators.0.result.value" in result["properties"]

    @oqt_vcr.use_cassette()
    def test_report_flatten_false(self):
        url = "/report?name={0}&dataset={1}&featureId={2}&flatten={3}".format(
            self.report_name,
            self.dataset,
            self.feature_id,
            False,
        )
        response = self.client.get(url)
        result = response.json()
        assert "report.result.value" not in result["properties"]
        assert "value" in result["properties"]["report"]["result"]
        assert "indicators.0.result.value" not in result["properties"]
        assert "value" in result["properties"]["indicators"][0]["result"]


if __name__ == "__main__":
    unittest.main()
