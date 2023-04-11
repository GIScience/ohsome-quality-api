import pytest


def test_metadata(
    client,
    response_template,
    building_count,
    metadata_mapping_saturation,
    metadata_report_minimal,
):
    response = client.get("/metadata")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    # check topics result
    assert building_count == next(
        filter(lambda t: t["key"] == "building_count", result["topics"])
    )
    # check indicators result
    # TODO: change to t["key"]
    assert metadata_mapping_saturation == next(
        filter(lambda t: t["name"] == "Mapping Saturation", result["indicators"])
    )
    # check reports result
    # TODO: change to t["key"]
    assert metadata_report_minimal == next(
        filter(lambda t: t["name"] == "Minimal", result["reports"])
    )


@pytest.mark.skip(reason="Not yet implemented")
def test_project_core(
    client, response_template, building_count, metadata_mapping_saturation
):
    response = client.get("/metadata?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    # check topics result
    assert building_count == next(
        filter(lambda t: t["key"] == "building_count", result["topics"])
    )
    # check indicators result
    # TODO: change to t["key"]
    assert metadata_mapping_saturation == next(
        filter(lambda t: t["name"] == "Mapping Saturation", result["indicators"])
    )
    # check reports result
    # no report in core yet


@pytest.mark.skip(reason="Not yet implemented")
def test_project_misc(
    client,
    response_template,
    metadata_topic_minimal,
    metadata_indicator_minimal,
    metadata_report_minimal,
):
    response = client.get("/metadata?project=misc")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    # check topics result
    assert metadata_topic_minimal == next(
        filter(lambda t: t["key"] == "minimal", result["topics"])
    )
    # check indicators result
    # TODO: change to t["key"]
    assert metadata_indicator_minimal == next(
        filter(lambda t: t["name"] == "Minimal", result["indicators"])
    )
    # check reports result
    # TODO: change to t["key"]
    assert metadata_report_minimal == next(
        filter(lambda t: t["name"] == "Minimal", result["reports"])
    )
