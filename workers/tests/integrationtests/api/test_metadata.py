def test_metadata(
    client,
    response_template,
    metadata_project_core,
    metadata_topic_building_count,
    metadata_indicator_mapping_saturation,
    metadata_report_multilevel_mapping_saturation,
    metadata_quality_dimension_completeness,
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
    # check quality dimensions result
    assert (
        metadata_quality_dimension_completeness["completeness"]
        == result["quality-dimensions"]["completeness"]
    )
    # check projects result
    assert metadata_project_core["core"] == result["projects"]["core"]
    # check indicators result
    assert (
        metadata_indicator_mapping_saturation["mapping-saturation"]
        == result["indicators"]["mapping-saturation"]
    )
    # check reports result
    assert (
        metadata_report_multilevel_mapping_saturation["multilevel-mapping-saturation"]
        == result["reports"]["multilevel-mapping-saturation"]
    )


def test_project_core(
    client,
    response_template,
):
    response = client.get("/metadata?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    for k in ("topics", "reports"):
        for p in result[k].values():
            assert p["project"] == "core"
    for k in ("indicators",):
        for p in result[k].values():
            assert "core" in p["projects"]
    # check topics result
    assert len(result["topics"]) > 0
    # check indicators result
    assert len(result["indicators"]) > 0
    # check reports result
    assert len(result["reports"]) > 0


def test_project_misc(
    client,
    response_template,
):
    response = client.get("/metadata?project=misc")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    for k in ("topics", "reports"):
        for p in result[k].values():
            assert p["project"] == "misc"
    for k in ("indicators",):
        for p in result[k].values():
            assert "misc" in p["projects"]
    # check topics result
    assert len(result["topics"]) > 0
    # check indicators result
    assert len(result["indicators"]) > 0
    # check reports result
    assert len(result["reports"]) > 0
