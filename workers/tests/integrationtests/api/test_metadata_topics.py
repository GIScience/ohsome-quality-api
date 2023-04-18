import pytest


def test_metadata_topic(client, response_template, metadata_topic_building_count):
    response = client.get("/metadata/topics")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_topic_building_count == result["building_count"]
    # TODO
    # assert "minimal" not in [topic["key"] for topic in result]


def test_metadata_topic_project_core(
    client, response_template, metadata_topic_building_count
):
    response = client.get("/metadata/topics/?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_topic_building_count == result["building_count"]
    assert "minimal" not in result.keys()


def test_metadata_topic_project_experimental(client, response_template):
    response = client.get("/metadata/topics/?project=experimental")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert "building_count" not in result.keys()
    assert "minimal" not in result.keys()


@pytest.mark.skip(reason="Not yet implemented")
def test_metadata_topic_project_not_found_error(client):
    response = client.get("/metadata/topics/?project=foo")
    assert response.status_code == 404  # Not Found
    # content = response.json()


def test_metadata_topic_by_key(
    client, response_template, metadata_topic_building_count
):
    response = client.get("/metadata/topics/building_count")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_topic_building_count


def test_metadata_topic_by_key_not_found_error(client):
    response = client.get("/metadata/topics/foo")
    assert response.status_code == 422
