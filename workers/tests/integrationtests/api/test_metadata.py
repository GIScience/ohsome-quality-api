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
    # TODO: add report when a core report is implemented


def test_project_core(
    client, response_template, building_count, metadata_mapping_saturation
):
    response = client.get("/metadata?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    for p in result["topics"] + result["indicators"] + result["reports"]:
        assert p["project"] == "core"
    # check topics result
    assert len(result["topics"]) > 0
    # check indicators result
    assert len(result["indicators"]) > 0
    # check reports result
    # no report in core yet


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
    for p in result["topics"] + result["indicators"] + result["reports"]:
        assert p["project"] == "misc"
    # check topics result
    assert len(result["topics"]) > 0
    # check indicators result
    assert len(result["indicators"]) > 0
    # check reports result
    assert len(result["reports"]) > 0
    # TODO: remove when a "core" report is implemented and added in test_metadata
    # TODO: change to t["key"]
    assert metadata_report_minimal == next(
        filter(lambda t: t["name"] == "Minimal", result["reports"])
    )
