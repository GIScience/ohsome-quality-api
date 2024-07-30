"""
Testing FastAPI Applications:
https://fastapi.tiangolo.com/tutorial/testing/

Shared tests for `/indicator` and `/report` endpoints using the `bpolys` parameter.
Tests for the individual endpoints and using the `bpolys` parameter please see:
    - `test_api_indicator_geojson_io.py`
    - `test_api_report_geojson_io.py`
"""

import os
from unittest import mock

import httpx

from tests.integrationtests.utils import AsyncMock


# TODO: could/should this be converted to a parameterized test?
def test_ohsome_timeout(client, bpolys):
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
    with mock.patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = httpx.Response(
            200,
            content=invalid_response,
            request=httpx.Request("POST", "https://www.example.org/"),
        )

        for endpoint, parameters in (
            (
                "/reports/minimal",
                {
                    "bpolys": bpolys,
                },
            ),
            (
                "/indicators/minimal",
                {
                    "bpolys": bpolys,
                    "topic": "minimal",
                    # TODO: would it be better to make the following parameter optional?
                    "attribute": "height",
                },
            ),
        ):
            response = client.post(endpoint, json=parameters)
            assert response.status_code == 422
            content = response.json()
            assert content["type"] == "OhsomeApiError"
