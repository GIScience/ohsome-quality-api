"""Tests for computing indicators.

Validate the response from requests to the `/indicators` endpoint of the API.
"""


from datetime import datetime, timedelta

import pytest
from schema import Optional, Or, Schema

from tests.integrationtests.utils import oqt_vcr
from tests.unittests.mapping_saturation.fixtures import VALUES_1 as DATA

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
                    "timestamp_oqt": str,
                    "timestamp_osm": Or(str),
                    "value": Or(float, str, int, None),
                    "label": str,
                    "description": str,
                    "figure": dict,
                    Optional("svg"): str,
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
                        "timestamp_oqt": str,
                        "timestamp_osm": Or(str),
                        "value": Or(float, str, int, None),
                        "label": str,
                        "description": str,
                        "figure": dict,
                        Optional("svg"): str,
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


def test_custom_data(client, bpolys, headers, schema):
    """Test parameter Topic with custom data attached."""
    endpoint = ENDPOINT + "mapping-saturation"
    timestamp_objects = [
        datetime(2020, 7, 17, 9, 10, 0) + timedelta(days=1 * x)
        for x in range(DATA.size)
    ]
    timestamp_iso_string = [t.strftime("%Y-%m-%dT%H:%M:%S") for t in timestamp_objects]
    # Data is ohsome API response result for the topic 'building-count' and the bpolys
    #   of for Heidelberg
    parameters = {
        "bpolys": bpolys,
        "topic": {
            "key": "foo",
            "name": "bar",
            "description": "",
            "data": {
                "result": [
                    {"value": v, "timestamp": t}
                    for v, t in zip(DATA, timestamp_iso_string)
                ]
            },
        },
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert schema.is_valid(response.json())

    parameters = {
        "bpolys": bpolys,
        "topic": {
            "key": "foo",
            "name": "bar",
            "description": "",
            "data": {"result": [{"value": 1.0}]},  # Missing timestamp item
        },
    }
    response = client.post(endpoint, json=parameters)
    assert response.status_code == 422


@oqt_vcr.use_cassette
def test_include_svg(client, bpolys, topic_key_minimal, headers, schema):
    endpoint = ENDPOINT + "minimal"
    parameters = {
        "topic": topic_key_minimal,
        "bpolys": bpolys,
        "includeSvg": True,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    content = response.json()
    assert schema.is_valid(content)
    if schema.name == "json":
        for result in content["result"]:
            assert "svg" in result["result"].keys()
    elif schema.name == "geojson":
        for feature in content["features"]:
            assert "svg" in feature["properties"]["result"].keys()
    else:
        raise ValueError("Unexpected schema name")

    parameters = {
        "topic": topic_key_minimal,
        "bpolys": bpolys,
        "includeSvg": False,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    content = response.json()
    assert schema.is_valid(content)
    if schema.name == "json":
        for result in content["result"]:
            assert "svg" not in result["result"].keys()
    elif schema.name == "geojson":
        for feature in content["features"]:
            assert "svg" not in feature["properties"]["result"].keys()
    else:
        raise ValueError("Unexpected schema name")

    parameters = {
        "topic": topic_key_minimal,
        "bpolys": bpolys,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    content = response.json()
    assert schema.is_valid(content)
    if schema.name == "json":
        for result in content["result"]:
            assert "svg" not in result["result"].keys()
    elif schema.name == "geojson":
        for feature in content["features"]:
            assert "svg" not in feature["properties"]["result"].keys()
    else:
        raise ValueError("Unexpected schema name")
