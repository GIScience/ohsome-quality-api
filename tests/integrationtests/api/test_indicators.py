"""Tests for computing indicators.

Validate the response from requests to the `/indicators` endpoint of the API.
"""


import pytest
from schema import Optional, Or, Schema

from tests.integrationtests.utils import get_geojson_fixture, oqt_vcr

ENDPOINT = "/indicators/"


RESPONSE_SCHEMA_JSON = Schema(
    schema={
        "apiVersion": str,
        "attribution": {
            "url": str,
            Optional("text"): str,
        },
        "results": [
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
                    "timestampOQT": str,
                    "timestampOSM": Or(str),
                    "value": Or(float, str, int, None),
                    "label": str,
                    "description": str,
                    "figure": dict,
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
                        "timestampOQT": str,
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


@pytest.fixture
def europe():
    return get_geojson_fixture("europe.geojson")


@oqt_vcr.use_cassette
@pytest.mark.parametrize(
    "indicator,topic",
    [
        ("minimal", "minimal"),
        ("mapping-saturation", "building-count"),
        ("currentness", "building-count"),
        ("attribute-completeness", "building-count"),
    ],
)
def test_indicators(
    client,
    bpolys,
    headers,
    schema,
    indicator,
    topic,
):
    """Minimal viable request for a single bpoly."""
    endpoint = ENDPOINT + indicator
    parameters = {
        "bpolys": bpolys,
        "topic": topic,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert schema.is_valid(response.json())


@oqt_vcr.use_cassette
def test_minimal_fc(
    client,
    feature_collection_germany_heidelberg_bahnstadt_bergheim,
    headers,
    schema,
):
    """Minimal viable request for multiple bpolys."""
    endpoint = ENDPOINT + "minimal"
    parameters = {
        "bpolys": feature_collection_germany_heidelberg_bahnstadt_bergheim,
        "topic": "minimal",
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert schema.is_valid(response.json())


def test_bpolys_size_limit(client, europe, headers, schema):
    endpoint = ENDPOINT + "minimal"
    parameters = {
        "bpolys": europe,
        "topic": "minimal",
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert response.status_code == 422
    content = response.json()
    assert content["type"] == "SizeRestrictionError"
