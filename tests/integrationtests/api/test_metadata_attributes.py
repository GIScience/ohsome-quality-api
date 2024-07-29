def test_metadata_attribute(
    client,
    response_template,
    response_metadata_attribute_clc_leaf_type,
):
    response = client.get("/metadata/attributes")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert (
        response_metadata_attribute_clc_leaf_type["clc-leaf-type"]
        == result["clc-leaf-type"]
    )
