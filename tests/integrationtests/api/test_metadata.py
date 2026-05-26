def test_metadata(
    client,
    response_template,
    metadata_topic_building_count,
    metadata_indicator_mapping_saturation,
    metadata_quality_dimension,
    metadata_attribute_clc_leaf_type,
):
    response = client.get("/metadata")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    # check topics result
    assert (
        metadata_topic_building_count["building-count"]
        == result["topics"]["building-count"]
    )
    # check quality dimensions result
    assert (
        metadata_quality_dimension["minimal"] == result["qualityDimensions"]["minimal"]
    )
    # check indicators result
    assert (
        metadata_indicator_mapping_saturation["mapping-saturation"]
        == result["indicators"]["mapping-saturation"]
    )
    assert (
        metadata_attribute_clc_leaf_type["clc-leaf-type"]
        == result["attributes"]["clc-leaf-type"]
    )
