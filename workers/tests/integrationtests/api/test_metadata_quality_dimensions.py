def test_metadata_quality_dimensions(
    client, response_template, metadata_quality_dimension_completeness
):
    response = client.get("/metadata/quality_dimensions")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert (
        metadata_quality_dimension_completeness["completeness"]
        == result["completeness"]
    )


def test_metadata_quality_dimensions_by_key(
    client, response_template, metadata_quality_dimension_completeness
):
    response = client.get("/metadata/quality_dimensions/completeness")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_quality_dimension_completeness


def test_metadata_quality_dimensions_by_key_not_found_error(client):
    response = client.get("/metadata/quality_dimensions/foo")
    assert response.status_code == 422
