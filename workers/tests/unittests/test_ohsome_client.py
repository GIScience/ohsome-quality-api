import asyncio
import os
from dataclasses import dataclass
from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import MagicMock, patch

import httpx
from schema import Optional, Schema

from ohsome_quality_analyst.ohsome import client as ohsome_client


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


@dataclass
class LayerDefinitionMock:
    name: str = ""
    description: str = ""
    endpoint: str = "elements/length"
    filter: str = "mock_filter"
    ratio_filter: str = None


class TestOhsomeClient(TestCase):
    def setUp(self) -> None:
        fixtures_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures"
        )
        fixture = os.path.join(fixtures_dir, "ohsome-response-200-invalid.geojson")
        with open(fixture, "r") as reader:
            self.invalid_geojson = reader.read()
        fixture = os.path.join(fixtures_dir, "ohsome-response-200-valid.geojson")
        with open(fixture, "r") as reader:
            self.valid_geojson = reader.read()
        self.layer = LayerDefinitionMock()
        self.bpolys = ""

    def test_query_valid_response(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.valid_geojson,
                request=httpx.Request("POST", "url"),
            )
            response = asyncio.run(ohsome_client.query(self.layer, self.bpolys))
            self.assertTrue(response.is_valid)

    def test_query_invalid_response_with_status_code_200(self) -> None:
        """When response is streamed it can be invalid while status code equals 200"""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.invalid_geojson,
                request=httpx.Request("POST", "url"),
            )
            with self.assertRaises(JSONDecodeError):
                asyncio.run(ohsome_client.query(self.layer, self.bpolys))

    def test_query_status_code_400(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                400,
                content=self.invalid_geojson,
                request=httpx.Request("POST", "url"),
            )
            with self.assertRaises(httpx.HTTPStatusError):
                asyncio.run(ohsome_client.query(self.layer, self.bpolys))

    def test_iso_time(self) -> None:
        with self.assertRaises(ValueError):
            ohsome_client.check_iso_time("")
            ohsome_client.check_iso_time("20140101")

        self.assertTrue(ohsome_client.check_iso_time("2014-01-01"))
        self.assertTrue(ohsome_client.check_iso_time("2007-01-25T12:00:00"))

        self.assertTrue(
            ohsome_client.check_iso_time("2014-01-01,2015-07-01,2018-10-10")
        )

        # TODO:
        # self.assertTrue(ohsome_client.check_iso_time("2007-01-25T12:00:00Z"))
        # self.assertTrue(ohsome_client.check_iso_time("2014-01-01/2018-01-01/P1Y"))

    def test_build_data_dict_minimal(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
            }
        )
        layer = LayerDefinitionMock()
        data = ohsome_client.build_data_dict(layer, "mock_bpolys")
        self.assertTrue(schema.is_valid(data))

    def test_build_data_dict_ratio(self) -> None:
        """Layer has no ratio filter definied"""
        layer = LayerDefinitionMock()
        with self.assertRaises(ValueError):
            ohsome_client.build_data_dict(layer, "mock_bpolys", ratio=True)

    def test_build_data_dict_ratio_2(self) -> None:
        """Layer has ratio filter definied"""
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
                "filter2": str,
            }
        )
        layer = LayerDefinitionMock()
        layer.ratio_filter = "mock_ratio_filter"
        data = ohsome_client.build_data_dict(layer, "mock_bpolys", ratio=True)
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
        layer = LayerDefinitionMock()
        data = ohsome_client.build_data_dict(layer, "mock_bpolys", time="2014-01-01")
        self.assertTrue(schema.is_valid(data))

        layer = LayerDefinitionMock()
        layer.ratio_filter = "mock_ratio_filter"
        data = ohsome_client.build_data_dict(layer, "mock_bpolys", time="2014-01-01")
        self.assertTrue(schema.is_valid(data))
