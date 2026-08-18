def test_metadata_attribute(
    client,
    response_template,
    metadata_attribute_forests,
):
    response = client.get("/metadata/attributes")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_attribute_forests["forests"] == result["forests"]
