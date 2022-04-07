import asyncio
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import geojson
import httpx
from schema import Optional, Schema

from ohsome_quality_analyst.base.layer import LayerData, LayerDefinition
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.utils.exceptions import (
    LayerDataSchemaError,
    OhsomeApiError,
    SchemaError,
)


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestOhsomeClient(TestCase):
    def setUp(self) -> None:
        fixtures_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures"
        )

        fixture = os.path.join(fixtures_dir, "ohsome-response-200-invalid.geojson")
        with open(fixture, "r") as reader:
            self.invalid_response_geojson = reader.read()
        fixture = os.path.join(fixtures_dir, "ohsome-response-200-valid.geojson")
        with open(fixture, "r") as reader:
            self.valid_response = reader.read()
        fixture = os.path.join(fixtures_dir, "ohsome-response-400-time.json")
        with open(fixture, "r") as reader:
            self.invalid_response_time = reader.read()

        fixture = os.path.join(fixtures_dir, "heidelberg-altstadt-geometry.geojson")
        with open(fixture, "r") as file:
            self.bpolys = geojson.load(file)
        self.layer = LayerDefinition(
            name="",
            description="",
            endpoint="elements/length",
            filter_="mock_filter",
        )
        self.ohsome_api = "https://api.ohsome.org/v1/"

    def test_query_valid_response(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.valid_response,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            response = asyncio.run(ohsome_client.query(self.layer, self.bpolys))
            self.assertDictEqual(response, geojson.loads(self.valid_response))

    def test_query_invalid_response_with_status_code_200(self) -> None:
        """When response is streamed it can be invalid while status code equals 200"""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.invalid_response_geojson,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            with self.assertRaises(OhsomeApiError):
                asyncio.run(ohsome_client.query(self.layer, self.bpolys))

    def test_query_status_code_400(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                400,
                content=self.invalid_response_time,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            with self.assertRaises(OhsomeApiError):
                asyncio.run(ohsome_client.query(self.layer, self.bpolys))

    def test_query_user_agent(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.valid_response,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            asyncio.run(ohsome_client.query(self.layer, self.bpolys))
            self.assertEqual(
                "ohsome-quality-analyst",
                mock_request.call_args[1]["headers"]["user-agent"].split("/")[0],
            )

    def test_build_url(self) -> None:
        ohsome_api = self.ohsome_api.rstrip("/")
        url = ohsome_client.build_url(self.layer)
        self.assertEqual(ohsome_api + "/elements/length", url)
        url = ohsome_client.build_url(self.layer, ratio=True)
        self.assertEqual(ohsome_api + "/elements/length/ratio", url)
        url = ohsome_client.build_url(self.layer, endpoint="foo/bar")
        self.assertEqual(ohsome_api + "/foo/bar", url)
        url = ohsome_client.build_url(self.layer, endpoint="foo/bar", ratio=True)
        self.assertEqual(ohsome_api + "/foo/bar/ratio", url)

    def test_build_data_dict_minimal(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
            }
        )
        data = ohsome_client.build_data_dict(self.layer, self.bpolys)
        self.assertTrue(schema.is_valid(data))

    def test_build_data_dict_ratio(self) -> None:
        """Layer has no ratio filter defined"""
        with self.assertRaises(ValueError):
            ohsome_client.build_data_dict(self.layer, self.bpolys, ratio=True)

    def test_build_data_dict_ratio_2(self) -> None:
        """Layer has ratio filter defined"""
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
                "filter2": str,
            }
        )
        layer = LayerDefinition(
            name="",
            description="",
            endpoint="elements/length",
            filter_="mock_filter",
            ratio_filter="mock_ratio_filter",
        )
        data = ohsome_client.build_data_dict(layer, self.bpolys, ratio=True)
        self.assertTrue(schema.is_valid(data))

    def test_build_data_with_time(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
                Optional("filter2"): str,
                "time": str,
            }
        )
        data = ohsome_client.build_data_dict(self.layer, self.bpolys, time="2014-01-01")
        self.assertTrue(schema.is_valid(data))
        layer = LayerDefinition(
            name="",
            description="",
            endpoint="elements/length",
            filter_="mock_filter",
            ratio_filter="mock_ratio_filter",
        )
        data = ohsome_client.build_data_dict(layer, self.bpolys, time="2014-01-01")
        self.assertTrue(schema.is_valid(data))

    def test_query_layer_data_valid_1(self):
        data = asyncio.run(
            ohsome_client.query(
                LayerData(
                    "name",
                    "description",
                    {
                        "result": [
                            {"value": 1.0, "timestamp": "2020-03-20T01:30:08.180856"}
                        ]
                    },
                )
            )
        )
        self.assertDictEqual(
            {"result": [{"value": 1.0, "timestamp": "2020-03-20T01:30:08.180856"}]},
            data,
        )

    def test_query_layer_data_valid_2(self):
        data = asyncio.run(
            ohsome_client.query(
                LayerData(
                    "name",
                    "description",
                    {
                        "result": [
                            {
                                "value": 1.0,
                                "fromTimestamp": "2020-03-20T01:30:08.180856",
                                "toTimestamp": "2020-03-20T01:30:08.180856",
                            }
                        ]
                    },
                )
            )
        )
        self.assertDictEqual(
            {
                "result": [
                    {
                        "value": 1.0,
                        "fromTimestamp": "2020-03-20T01:30:08.180856",
                        "toTimestamp": "2020-03-20T01:30:08.180856",
                    }
                ]
            },
            data,
        )

    def test_query_layer_data_invalid_empty(self):
        with self.assertRaises(LayerDataSchemaError):
            asyncio.run(ohsome_client.query(LayerData("name", "description", {})))

    def test_query_layer_data_invalid_empty_list(self):
        with self.assertRaises(LayerDataSchemaError):
            asyncio.run(
                ohsome_client.query(LayerData("name", "description", {"result": []}))
            )

    def test_query_layer_data_invalid_missing_key(self):
        with self.assertRaises(LayerDataSchemaError):
            asyncio.run(
                ohsome_client.query(
                    LayerData("name", "description", {"result": [{"value": 1.0}]})
                )
            )

    def test_validate_query_results_valid_1(self):
        ohsome_client.validate_query_results(
            {"result": [{"value": 1.0, "timestamp": "2020-03-20T01:30:08.180856"}]}
        )

    def test_validate_query_results_valid_2(self):
        ohsome_client.validate_query_results(
            {
                "result": [
                    {
                        "value": 1.0,
                        "fromTimestamp": "2020-03-20T01:30:08.180856",
                        "toTimestamp": "2020-03-20T01:30:08.180856",
                    }
                ]
            }
        )

    def test_validate_query_results_invalid_empyt(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({})

    def test_validate_query_results_invalid_empyt_list(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({"result": []})

    def test_validate_query_results_invalid_missing_key(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results(
                {"result": [{"value": 1.0}]}  # Missing timestamp item
            )

    def test_validate_query_results_valid_ratio(self):
        ohsome_client.validate_query_results(
            {
                "ratioResult": [
                    {
                        "ratio": 1.0,
                        "value": 1.0,
                        "value2": 1.0,
                        "timestamp": "2020-03-20T01:30:08.180856",
                    }
                ]
            },
            ratio=True,
        )

    def test_validate_query_results_valid_ratio_2(self):
        ohsome_client.validate_query_results(
            {
                "ratioResult": [
                    {
                        "ratio": "NaN",
                        "value": 1.0,
                        "value2": 1.0,
                        "timestamp": "2020-03-20T01:30:08.180856",
                    }
                ]
            },
            ratio=True,
        )

    def test_validate_query_results_invalid_empyt_ratio(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({}, ratio=True)

    def test_validate_query_results_invalid_empyt_list_ratio(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({"ratioResult": []}, ratio=True)

    def test_validate_query_results_invalid_missing_key_ratio(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results(
                {"ratioResult": [{"value": 1.0}]}, ratio=True  # Missing timestamp item
            )
