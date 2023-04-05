import pytest


@pytest.fixture
def metadata_minimal():
    return {
        "name": "Minimal",
        "description": "An minimal Indicator for testing purposes.",
    }


@pytest.fixture
def metadata_mapping_saturation():
    return {
        "name": "Mapping Saturation",
        "description": (
            "Calculate if mapping has saturated. High saturation has been reached if "
            + "the growth of the fitted curve is minimal."
        ),
    }


def test(client, response_template, metadata_mapping_saturation):
    response = client.get("/metadata/indicators/")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_mapping_saturation == next(
        filter(lambda r: r["name"] == "Mapping Saturation", result)
    )


def test_by_key(client, response_template, metadata_minimal):
    response = client.get("/metadata/indicators/minimal")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_minimal


def test_by_key_not_found_error(client):
    response = client.get("/metadata/indicators/foo")
    assert response.status_code == 422


@pytest.mark.skip(reason="Not yet implemented")
def test_project_core(client, response_template, metadata_mapping_saturation):
    response = client.get("/metadata/indicators/?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_mapping_saturation == next(
        filter(lambda r: r["name"] == "Mapping Saturation", result)
    )
    assert "Minimal" not in [r["name"] for r in result]


@pytest.mark.skip(reason="Not yet implemented")
def test_project_not_found_error(client):
    response = client.get("/metadata/indicators/?project=foo")
    assert response.status_code == 404  # Not Found
    # content = response.json()
