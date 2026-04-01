import json

import geojson
import pytest

from ohsome_quality_api.indicators.definitions import IndicatorEnum


def test(client, response_template, metadata_indicator_mapping_saturation):
    response = client.get("/metadata/indicators/")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert (
        metadata_indicator_mapping_saturation["mapping-saturation"]
        == result["mapping-saturation"]
    )
    assert "minimal" not in result


def test_by_key(client, response_template, metadata_indicator_minimal):
    response = client.get("/metadata/indicators/minimal")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_indicator_minimal


def test_by_key_not_found_error(client):
    response = client.get("/metadata/indicators/foo")
    assert response.status_code == 422


def test_project_core(client, response_template, metadata_indicator_mapping_saturation):
    response = client.get("/metadata/indicators/?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert (
        metadata_indicator_mapping_saturation["mapping-saturation"]
        == result["mapping-saturation"]
    )
    assert "minimal" not in result


def test_project_all(
    client,
    response_template,
):
    response = client.get("/metadata/indicators/?project=all")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert len(result) == len(IndicatorEnum)


@pytest.mark.skip(reason="Not yet implemented")
def test_project_not_found_error(client):
    response = client.get("/metadata/indicators/?project=foo")
    assert response.status_code == 404  # Not Found


def test_coverage_default(client):
    response = client.get("metadata/indicators/mapping-saturation/coverage")
    assert response.status_code == 200
    assert response.json()["features"][0]["geometry"] == {
        "coordinates": [
            [
                [-180, 90],
                [-180, -90],
                [180, -90],
                [180, 90],
                [-180, 90],
            ]
        ],
        "type": "Polygon",
    }


@pytest.mark.skip(reason="Depends on database")
def test_coverage(client):
    response = client.get("metadata/indicators/building-comparison/coverage")
    assert response.status_code == 200
    result = geojson.loads(json.dumps(response.json()))
    assert result.is_valid
    assert isinstance(result, geojson.FeatureCollection)


@pytest.mark.skip(reason="Depends on database")
def test_coverage_land_cover_thematic_accuracy(client):
    response = client.get("metadata/indicators/land-cover-thematic-accuracy/coverage")
    assert response.status_code == 200
    result = geojson.loads(json.dumps(response.json()))
    assert result.is_valid
    assert isinstance(result, geojson.FeatureCollection)
