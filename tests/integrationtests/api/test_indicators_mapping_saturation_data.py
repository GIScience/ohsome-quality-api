from datetime import datetime, timedelta

from schema import Optional, Or, Schema

from tests.unittests.mapping_saturation.fixtures import VALUES_1 as DATA

ENDPOINT = "/indicators/mapping-saturation/data"


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
                    "figure": dict,
                },
            }
        ],
    },
    name="json",
    ignore_extra_keys=True,
)


def test_mapping_saturation_data(client, bpolys):
    """Test parameter Topic with custom data attached."""
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
                    for v, t in zip(DATA, timestamp_iso_string, strict=False)
                ]
            },
        },
    }
    response = client.post(ENDPOINT, json=parameters)
    assert RESPONSE_SCHEMA_JSON.is_valid(response.json())


def test_mapping_saturation_data_invalid(client, bpolys):
    parameters = {
        "bpolys": bpolys,
        "topic": {
            "key": "foo",
            "name": "bar",
            "description": "",
            "data": {"result": [{"value": 1.0}]},  # Missing timestamp item
        },
    }
    response = client.post(ENDPOINT, json=parameters)
    assert response.status_code == 422
