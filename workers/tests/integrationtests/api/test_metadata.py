def test_metadata(
    client,
    response_template,
    metadata_topic_building_count,
    metadata_indicator_mapping_saturation,
):
    response = client.get("/metadata")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    # check topics result
    assert (
        metadata_topic_building_count["building_count"]
        == result["topics"]["building_count"]
    )
    # check indicators result
    assert (
        metadata_indicator_mapping_saturation["mapping-saturation"]
        == result["indicators"]["mapping-saturation"]
    )
    # check reports result
    # TODO: add report when a core report is implemented


def test_project_core(
    client,
    response_template,
):
    response = client.get("/metadata?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    for k in ("topics", "indicators", "reports"):
        for p in result[k].values():
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
    metadata_report_minimal,
):
    response = client.get("/metadata?project=misc")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    for k in ("topics", "indicators", "reports"):
        for p in result[k].values():
            assert p["project"] == "misc"
    # check topics result
    assert len(result["topics"]) > 0
    # check indicators result
    assert len(result["indicators"]) > 0
    # check reports result
    assert len(result["reports"]) > 0
    # TODO: remove when a "core" report is implemented and added in test_metadata
    assert metadata_report_minimal["minimal"] == result["reports"]["minimal"]
