def test_metadata_topic(
    client,
    response_template,
    metadata_topic_building_count,
):
    response = client.get("/metadata/topics")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_topic_building_count["building-count"] == result["building-count"]
    assert "minimal" not in result


def test_metadata_topic_by_key(
    client,
    response_template,
    metadata_topic_building_count,
):
    response = client.get("/metadata/topics/building-count")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_topic_building_count


def test_metadata_topic_by_key_not_found_error(client):
    response = client.get("/metadata/topics/foo")
    assert response.status_code == 422
