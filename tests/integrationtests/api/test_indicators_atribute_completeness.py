import pytest

from ohsome_quality_api.attributes.definitions import get_attributes
from tests.integrationtests.api.test_indicators import (
    RESPONSE_SCHEMA_GEOJSON,
    RESPONSE_SCHEMA_JSON,
)
from tests.integrationtests.utils import oqapi_vcr

ENDPOINT = "/indicators/"
# global param for all tests of this module
pytestmark = pytest.mark.parametrize(
    "headers,schema",
    [
        ({"accept": "application/json"}, RESPONSE_SCHEMA_JSON),
        ({"accept": "application/geo+json"}, RESPONSE_SCHEMA_GEOJSON),
    ],
)


@oqapi_vcr.use_cassette
def test_indicators_attribute_completeness_single_attribute(
    client,
    bpolys,
    headers,
    schema,
    attribute_key,
):
    endpoint = ENDPOINT + "attribute-completeness"
    parameters = {
        "bpolys": bpolys,
        "topic": "building-count",
        "attributes": [attribute_key],
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert schema.is_valid(response.json())


@oqapi_vcr.use_cassette
def test_indicators_attribute_completeness_multiple_attributes(
    client,
    bpolys,
    headers,
    schema,
    attribute_key_multiple,
):
    endpoint = ENDPOINT + "attribute-completeness"
    parameters = {
        "bpolys": bpolys,
        "topic": "building-count",
        "attributes": attribute_key_multiple,
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert schema.is_valid(response.json())


def test_indicators_attribute_completeness_without_attribute(
    client,
    bpolys,
    headers,
    schema,
):
    endpoint = ENDPOINT + "attribute-completeness"
    parameters = {
        "bpolys": bpolys,
        "topic": "building-count",
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert response.status_code == 422
    content = response.json()
    assert content["type"] == "RequestValidationError"


def test_indicators_attribute_completeness_with_invalid_attribute_for_topic(
    client,
    bpolys,
    headers,
    schema,
):
    endpoint = ENDPOINT + "attribute-completeness"
    parameters = {
        "bpolys": bpolys,
        "topic": "building-count",
        # the following attribute is not valid for topic 'building-count'
        "attributes": ["maxspeed"],
    }
    response = client.post(endpoint, json=parameters, headers=headers)
    assert response.status_code == 422
    content = response.json()

    message = content["detail"][0]["msg"]
    all_attributes_for_topic = [
        attribute for attribute in (get_attributes()["building-count"])
    ]

    expected = (
        "Invalid combination of attribute and topic: maxspeed and building-count. "
        "Topic 'building-count' supports these attributes: {}"
    ).format(all_attributes_for_topic)

    assert message == expected
    assert content["type"] == "AttributeTopicCombinationError"
