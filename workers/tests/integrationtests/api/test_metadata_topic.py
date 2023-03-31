import pytest


@pytest.fixture
def building_count():
    return {
        "key": "building_count",
        "name": "Building Count",
        "description": (
            "All buildings as defined by all objects tagged with 'building=*'.\n"
        ),
        "endpoint": "elements/count",
        "filter": "building=* and building!=no and geometry:polygon",
        "indicators": ["mapping-saturation", "currentness", "attribute-completeness"],
        "ratio_filter": (
            "building=* and building!=no and geometry:polygon and height=* or "
            + "building:levels=*"
        ),
        "project": "core",
        "source": None,  # TODO: Should not be in response if None
    }


def test_metadata_topic(client, response_template, building_count):
    response = client.get("/metadata/topics")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert building_count == next(
        filter(lambda t: t["key"] == "building_count", result)
    )
    # TODO
    # assert "minimal" not in [topic["key"] for topic in result]


@pytest.mark.skip(reason="Not yet implemented")
def test_metadata_topic_project_core(client, response_template, building_count):
    response = client.get("/metadata/topics/?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert building_count == next(
        filter(lambda t: t["key"] == "building_count", result)
    )
    assert "minimal" not in [topic["key"] for topic in result]


@pytest.mark.skip(reason="Not yet implemented")
def test_metadata_topic_project_experimental(client, response_template):
    response = client.get("/metadata/topics/?project=experimental")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert "building_count" not in [topic["key"] for topic in result]
    assert "minimal" not in [topic["key"] for topic in result]


@pytest.mark.skip(reason="Not yet implemented")
def test_metadata_topic_project_not_found_error(client):
    response = client.get("/metadata/topics/?project=foo")
    assert response.status_code == 404  # Not Found
    # content = response.json()


def test_metadata_topic_by_key(client, response_template, building_count):
    response = client.get("/metadata/topics/building_count")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == building_count


def test_metadata_topic_by_key_not_found_error(client):
    response = client.get("/metadata/topics/foo")
    assert response.status_code == 422
