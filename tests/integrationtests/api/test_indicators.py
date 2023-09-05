"""Tests for computing indicators.

Validate the response from requests to the `/indicators` endpoint of the API.
"""

import pytest
from schema import Optional, Or, Schema

from tests.integrationtests.utils import oqapi_vcr

ENDPOINT = "/indicators/"

RESPONSE_SCHEMA_JSON = Schema(
    schema={
        "apiVersion": str,
        "attribution": {
            "url": str,
            Optional("text"): str,
        },
        "result": [
            {
                Optional("id"): Or(str, int),
                "metadata": {
                    "name": str,
                    "description": str,
                },
                "topic": {
                    "name": str,
                    "description": str,
                },
                "result": {
                    "timestamp": str,
                    "timestampOSM": Or(str),
                    "value": Or(float, str, int, None),
                    "label": str,
                    "description": str,
                    Optional("figure"): dict,
                },
            }
        ],
    },
    name="json",
    ignore_extra_keys=True,
)

RESPONSE_SCHEMA_GEOJSON = Schema(
    schema={
        "apiVersion": str,
        "attribution": {
            "url": str,
            Optional("text"): str,
        },
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": dict,
                Optional("id"): Or(str, int),
                "properties": {
                    "metadata": {
                        "name": str,
                        "description": str,
                    },
                    "topic": {
                        "name": str,
                        "description": str,
                    },
                    "result": {
                        "timestamp": str,
                        "timestampOSM": Or(str),
                        "value": Or(float, str, int, None),
                        "label": str,
                        "description": str,
                        "figure": dict,
                    },
                },
            }
        ],
    },
    name="geojson",
    ignore_extra_keys=True,
)

# global param for all tests of this module
pytestmark = pytest.mark.parametrize(
    "headers,schema",
    [
        ({"accept": "application/json"}, RESPONSE_SCHEMA_JSON),
        ({"accept": "application/geo+json"}, RESPONSE_SCHEMA_GEOJSON),
    ],
)


@oqapi_vcr.use_cassette
@pytest.mark.parametrize(
    "indicator,topic",
    [
        ("minimal", "minimal"),
        ("mapping-saturation", "building-count"),
        ("currentness", "building-count"),
    ],
)
def test_indicators(
    client,
    feature_collection_germany_heidelberg,
    headers,
    schema,
    indicator,
    topic,
):
    """Minimal viable request for a single bpoly."""
    endpoint = ENDPOINT + indicator
    parameters = {
        "bpolys": feature_collection_germany_heidelberg.model_dump(),
        "topic": topic,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert schema.is_valid(response.json())


@oqapi_vcr.use_cassette
def test_minimal_fc(
    client,
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
    headers,
    schema,
):
    geojson = feature_collection_heidelberg_bahnstadt_bergheim_weststadt.model_dump()
    """Minimal viable request for multiple bpolys."""
    endpoint = ENDPOINT + "minimal"
    parameters = {
        "bpolys": geojson,
        "topic": "minimal",
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert schema.is_valid(response.json())


@oqapi_vcr.use_cassette
def test_minimal_include_figure_true(
    client,
    feature_collection_germany_heidelberg,
    headers,
    schema,
):
    endpoint = ENDPOINT + "minimal"
    parameters = {
        "bpolys": feature_collection_germany_heidelberg.model_dump(),
        "topic": "minimal",
        "includeFigure": True,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    content = response.json()
    if schema == RESPONSE_SCHEMA_JSON:
        assert content["result"][0]["result"]["figure"] is not None
    elif schema == RESPONSE_SCHEMA_GEOJSON:
        assert content["features"][0]["properties"]["result"]["figure"] is not None
    else:
        raise AssertionError()


@oqapi_vcr.use_cassette
def test_minimal_include_figure_false(
    client,
    feature_collection_germany_heidelberg,
    headers,
    schema,
):
    endpoint = ENDPOINT + "minimal"
    parameters = {
        "bpolys": feature_collection_germany_heidelberg.model_dump(),
        "topic": "minimal",
        "includeFigure": False,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    content = response.json()
    if schema == RESPONSE_SCHEMA_JSON:
        assert content["result"][0]["result"]["figure"] is None
    elif schema == RESPONSE_SCHEMA_GEOJSON:
        assert content["features"][0]["properties"]["result"]["figure"] is None
    else:
        raise AssertionError()


def test_bpolys_size_limit(client, europe, headers, schema):
    endpoint = ENDPOINT + "minimal"
    parameters = {
        "bpolys": europe.model_dump(),
        "topic": "minimal",
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert response.status_code == 422
    content = response.json()
    assert content["type"] == "SizeRestrictionError"
