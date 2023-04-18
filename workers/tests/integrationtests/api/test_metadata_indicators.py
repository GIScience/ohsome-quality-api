import pytest


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
    assert "minimal" not in result.keys()


@pytest.mark.skip(reason="Not yet implemented")
def test_project_not_found_error(client):
    response = client.get("/metadata/indicators/?project=foo")
    assert response.status_code == 404  # Not Found
    # content = response.json()
