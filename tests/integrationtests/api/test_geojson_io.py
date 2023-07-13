"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/

Shared tests for `/indicator` and `/report` endpoints using the `bpolys` parameter.
Tests for the individual endpoints and using the `bpolys` parameter please see:
    - `test_api_indicator_geojson_io.py`
    - `test_api_report_geojson_io.py`
"""
import os
import unittest
from unittest import mock

import httpx
from fastapi.testclient import TestClient

from ohsome_quality_analyst.api.api import app
from tests.integrationtests.utils import AsyncMock, get_geojson_fixture


class TestApiReportIo(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ohsome_timeout(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "unittests",
            "fixtures",
            "ohsome-response-200-invalid.geojson",
        )
        with open(path, "r") as f:
            invalid_response = f.read()
        featurecollection = get_geojson_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson"
        )
        with mock.patch(
            "httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=invalid_response,
                request=httpx.Request("POST", "https://www.example.org/"),
            )

            for endpoint, parameters in (
                (
                    "/reports/minimal",
                    {
                        "bpolys": featurecollection,
                    },
                ),
                (
                    "/indicators/minimal",
                    {
                        "bpolys": featurecollection,
                        "topic": "minimal",
                    },
                ),
            ):
                response = self.client.post(endpoint, json=parameters)
                self.assertEqual(response.status_code, 422)
                content = response.json()
                self.assertEqual(content["type"], "OhsomeApiError")
