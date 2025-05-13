import json

import pytest
from approvaltests import Options, verify_as_json

from tests.approvaltests_namers import PytestNamer
from tests.conftest import FIXTURE_DIR
from tests.integrationtests.api.test_indicators import (
    RESPONSE_SCHEMA_GEOJSON,
    RESPONSE_SCHEMA_JSON,
)
from tests.integrationtests.utils import oqapi_vcr

ENDPOINT = "/indicators/land-cover-thematic-accuracy"


@pytest.fixture
def mock_db_fetch(monkeypatch):
    async def fetch(*_):
        with open(
            FIXTURE_DIR / "land-cover-thematic-accuracy-db-fetch-results.json", "r"
        ) as file:
            return json.load(file)

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator.client.fetch",
        fetch,
    )


@oqapi_vcr.use_cassette
@pytest.mark.parametrize(
    "headers,schema",
    [
        ({"accept": "application/json"}, RESPONSE_SCHEMA_JSON),
        ({"accept": "application/geo+json"}, RESPONSE_SCHEMA_GEOJSON),
    ],
)
def test_multi_class(client, bpolys, headers, schema, mock_db_fetch):
    # corine class parameter is optional (default all corine classes)
    parameters = {"bpolys": bpolys, "topic": "lulc"}
    response = client.post(ENDPOINT, json=parameters, headers=headers)
    assert response.status_code == 200
    assert schema.is_valid(response.json())


@oqapi_vcr.use_cassette
@pytest.mark.parametrize(
    "headers,schema",
    [
        ({"accept": "application/json"}, RESPONSE_SCHEMA_JSON),
        ({"accept": "application/geo+json"}, RESPONSE_SCHEMA_GEOJSON),
    ],
)
def test_single_class(client, bpolys, headers, schema, mock_db_fetch):
    # Corine class 23 are Pastures
    parameters = {"bpolys": bpolys, "topic": "lulc", "corineClass": "23"}
    response = client.post(ENDPOINT, json=parameters, headers=headers)
    assert response.status_code == 200
    assert schema.is_valid(response.json())


def test_invalid_topic(client, bpolys):
    parameters = {"bpolys": bpolys, "topic": "building-count"}
    response = client.post(ENDPOINT, json=parameters)
    assert response.status_code == 422
    verify_as_json(response.json(), options=Options().with_namer(PytestNamer()))


def test_invalid_class(client, bpolys):
    parameters = {"bpolys": bpolys, "topic": "lulc", "corineClass": "1"}
    response = client.post(ENDPOINT, json=parameters)
    assert response.status_code == 422
    verify_as_json(response.json(), options=Options().with_namer(PytestNamer()))
