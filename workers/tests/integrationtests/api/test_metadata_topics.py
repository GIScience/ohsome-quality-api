import pytest

from ohsome_quality_analyst.api.request_models import TopicEnum


def test_metadata_topic(client, response_template, metadata_topic_building_count):
    response = client.get("/metadata/topics")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_topic_building_count["building-count"] == result["building-count"]
    assert "minimal" not in result.keys()


def test_metadata_topic_project_core(
    client, response_template, metadata_topic_building_count
):
    response = client.get("/metadata/topics/?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_topic_building_count["building-count"] == result["building-count"]
    assert "minimal" not in result.keys()


def test_metadata_topic_project_experimental(client, response_template):
    response = client.get("/metadata/topics/?project=experimental")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert "building-count" not in result.keys()
    assert "minimal" not in result.keys()


def test_project_all(
    client,
    response_template,
):
    response = client.get("/metadata/topics/?project=all")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert len(result) == len(TopicEnum)


@pytest.mark.skip(reason="Not yet implemented")
def test_metadata_topic_project_not_found_error(client):
    response = client.get("/metadata/topics/?project=foo")
    assert response.status_code == 404  # Not Found
    # content = response.json()


def test_metadata_topic_by_key(
    client, response_template, metadata_topic_building_count
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
