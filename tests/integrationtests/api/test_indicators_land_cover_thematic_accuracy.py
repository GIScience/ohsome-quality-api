import json

import pytest
from pytest_approval.main import verify_json

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


@pytest.fixture
def mock_cov_geom(monkeypatch):
    async def fake_coverage(cls, inverse=False):
        return 100

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator.get_covered_area",
        fake_coverage,
    )


@oqapi_vcr.use_cassette
@pytest.mark.parametrize(
    "headers,schema",
    [
        ({"accept": "application/json"}, RESPONSE_SCHEMA_JSON),
        ({"accept": "application/geo+json"}, RESPONSE_SCHEMA_GEOJSON),
    ],
)
def test_multi_class(client, bpolys, headers, schema, mock_db_fetch, mock_cov_geom):
    # corine class parameter is optional (default all corine classes)
    parameters = {"bpolys": bpolys, "topic": "land-cover"}
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
def test_single_class(client, bpolys, headers, schema, mock_db_fetch, mock_cov_geom):
    # Corine class 23 are Pastures
    parameters = {"bpolys": bpolys, "topic": "land-cover", "corineLandCoverClass": "23"}
    response = client.post(ENDPOINT, json=parameters, headers=headers)
    assert response.status_code == 200
    assert schema.is_valid(response.json())


def test_invalid_topic(client, bpolys):
    parameters = {"bpolys": bpolys, "topic": "building-count"}
    response = client.post(ENDPOINT, json=parameters)
    assert response.status_code == 422
    assert verify_json(response.json())


def test_invalid_class(client, bpolys):
    parameters = {"bpolys": bpolys, "topic": "land-cover", "corineLandCoverClass": "1"}
    response = client.post(ENDPOINT, json=parameters)
    assert response.status_code == 422
    assert verify_json(response.json())
