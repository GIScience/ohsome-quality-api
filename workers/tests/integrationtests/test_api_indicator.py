"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/

For tests regarding the `bpolys` parameter see `test_api_indicator_geojson_io.py`.
"""
import unittest
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from schema import Schema

from ohsome_quality_analyst.api.api import app

from .api_response_schema import get_general_schema, get_indicator_feature_schema
from .utils import oqt_vcr

ENDPOINT = "/indicator"


class TestApiIndicator(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.indicator_name = "Minimal"
        self.layer_key = "minimal"
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = "3"
        self.fid_field = "ogc_fid"

        self.general_schema = get_general_schema()
        self.feature_schema = get_indicator_feature_schema()

    def run_tests(self, response) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/geo+json")
        for schema in (self.general_schema, self.feature_schema):
            self.validate(response.json(), schema)

    def validate(self, geojson: dict, schema: Schema) -> None:
        schema.validate(geojson)  # Print information if validation fails
        self.assertTrue(schema.is_valid(geojson))

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_default_fid_field(self):
        parameters = {
            "name": self.indicator_name,
            "layer_key": self.layer_key,
            "dataset": self.dataset,
            "featureId": self.feature_id,
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.run_tests(response)

    @oqt_vcr.use_cassette()
    def test_indicator_dataset_custom_fid_field(self):
        parameters = {
            "name": self.indicator_name,
            "layer_key": self.layer_key,
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
    def test_indicator_dataset_custom_fid_field_2(self):
        parameters = {
            "name": self.indicator_name,
            "layer_key": self.layer_key,
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
    def test_indicator_dataset_invalid(self):
        parameters = {
            "name": self.indicator_name,
            "layer_key": self.layer_key,
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
                "name": self.indicator_name,
                "layer_key": "building_count",
                "dataset": "regions",
            },
            {
                "name": self.indicator_name,
                "layer_key": "building_count",
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
    def test_indicator_include_svg_true(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&fidField={4}&includeSvg={5}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                self.fid_field,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "svg" in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_include_svg_false(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&fidField={4}&includeSvg={5}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                self.fid_field,
                False,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "svg" not in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_include_svg_default(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&fidField={4}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                self.fid_field,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "svg" not in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_invalid_layer(self):
        parameters = {
            "name": self.indicator_name,
            "layer_key": "amenities",
            "dataset": "regions",
            "featureId": "3",
        }
        for response in (
            self.client.get(ENDPOINT + "?" + urlencode(parameters)),
            self.client.post(ENDPOINT, json=parameters),
        ):
            self.assertEqual(response.status_code, 422)
            content = response.json()
            self.assertEqual(content["type"], "RequestValidationError")

    @oqt_vcr.use_cassette()
    def test_indicator_include_html_true(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&fidField={4}&includeHtml={5}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                self.fid_field,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "html" in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_include_html_false(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&fidField={4}&includeHtml={5}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                self.fid_field,
                False,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "html" not in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_include_html_default(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&fidField={4}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                self.fid_field,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "html" not in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_flatten_default(self):
        url = "/indicator?name={0}&layer_key={1}&dataset={2}&featureId={3}".format(
            self.indicator_name,
            self.layer_key,
            self.dataset,
            self.feature_id,
        )
        response = self.client.get(url)
        result = response.json()
        # Check flat result value
        assert "result.value" not in result["properties"]
        assert "value" in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_flatten_true(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&flatten={4}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "result.value" in result["properties"]

    @oqt_vcr.use_cassette()
    def test_indicator_flatten_false(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&flatten={4}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                False,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "result.value" not in result["properties"]
        assert "value" in result["properties"]["result"]

    @oqt_vcr.use_cassette()
    def test_indicator_include_data_default(self):
        url = "/indicator?name={0}&layer_key={1}&dataset={2}&featureId={3}".format(
            self.indicator_name,
            self.layer_key,
            self.dataset,
            self.feature_id,
        )
        response = self.client.get(url)
        result = response.json()
        assert "data" not in result["properties"]

    @oqt_vcr.use_cassette()
    def test_indicator_include_data_true(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&includeData={4}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                True,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "data" in result["properties"]

    @oqt_vcr.use_cassette()
    def test_indicator_include_data_false(self):
        url = (
            "/indicator?name={0}&layer_key={1}&dataset={2}"
            "&featureId={3}&includeData={4}".format(
                self.indicator_name,
                self.layer_key,
                self.dataset,
                self.feature_id,
                False,
            )
        )
        response = self.client.get(url)
        result = response.json()
        assert "data" not in result["properties"]


if __name__ == "__main__":
    unittest.main()
