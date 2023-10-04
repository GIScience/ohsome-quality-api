def test_metadata_quality_dimensions(
    client, response_template, metadata_quality_dimension
):
    response = client.get("/metadata/quality-dimensions")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_quality_dimension["minimal"] == result["minimal"]


def test_metadata_quality_dimensions_by_key(
    client, response_template, metadata_quality_dimension
):
    response = client.get("/metadata/quality-dimensions/minimal")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_quality_dimension


def test_metadata_quality_dimensions_by_key_not_found_error(client):
    response = client.get("/metadata/quality-dimensions/foo")
    assert response.status_code == 422
