def test_metadata(
    client,
    response_template,
    metadata_topic_buildings,
    metadata_indicator_mapping_saturation,
    metadata_quality_dimension,
    metadata_attribute_forests,
):
    response = client.get("/metadata")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    # check topics result
    assert metadata_topic_buildings["buildings"] == result["topics"]["buildings"]
    # check quality dimensions result
    assert (
        metadata_quality_dimension["completeness"]
        == result["qualityDimensions"]["completeness"]
    )
    # check indicators result
    assert (
        metadata_indicator_mapping_saturation["mapping-saturation"]
        == result["indicators"]["mapping-saturation"]
    )
    assert metadata_attribute_forests["forests"] == result["attributes"]["forests"]
