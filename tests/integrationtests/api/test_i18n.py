import os

import pytest
from approvaltests import verify

from ohsome_quality_api.utils.helper import get_project_root
from tests.approvaltests_namers import PytestNamer

ENDPOINT = "/indicators/"

# TODO: Remove and recreate VCR cassette for this test


@pytest.fixture
def indicator(client, bpolys, monkeypatch):
    monkeypatch.setenv(
        "FASTAPI_I18N_LOCALE_DIR",
        os.path.join(get_project_root(), "ohsome_quality_api/locale"),
    )
    endpoint = "/indicators/mapping-saturation"
    parameters = {
        "bpolys": bpolys,
        "topic": "building-count",
    }
    response = client.post(
        endpoint,
        json=parameters,
        headers={
            "Accept-Language": "de",
            "accept": "application/json",
        },
    )
    return response.json()


def test_translation_indicator_metadata_description(indicator):
    verify(indicator["result"][0]["metadata"]["description"], namer=PytestNamer())


def test_translation_indicator_result_description(indicator):
    """Test successful translation of result description.

    Result description are string templates. This tests checks if translations
    of string templates is working as expected.
    """
    verify(indicator["result"][0]["result"]["description"], namer=PytestNamer())
