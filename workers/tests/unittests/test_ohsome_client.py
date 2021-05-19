import asyncio
import os
from dataclasses import dataclass
from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import MagicMock, patch

import httpx

from ohsome_quality_analyst.ohsome import client as ohsome_client


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


@dataclass
class LayerDefinitionMock:
    name: str = ""
    description: str = ""
    endpoint: str = "elements/length"
    filter: str = ""
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
                request=httpx.Request("POST", "mock.org"),
            )
            response = asyncio.run(ohsome_client.query(self.layer, self.bpolys))
            self.assertTrue(response.is_valid)

    def test_query_invalid_response_with_status_code_200(self) -> None:
        """When response is streamed it can be invalid while status code equals 200"""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.invalid_geojson,
                request=httpx.Request("POST", "mock.org"),
            )
            with self.assertRaises(JSONDecodeError):
                asyncio.run(ohsome_client.query(self.layer, self.bpolys))

    def test_query_status_code_400(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                400,
                content=self.invalid_geojson,
                request=httpx.Request("POST", "mock.org"),
            )
            with self.assertRaises(httpx.HTTPStatusError):
                asyncio.run(ohsome_client.query(self.layer, self.bpolys))
