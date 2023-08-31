from ohsome_quality_api.reports.definitions import ReportEnum


def test(client, response_template, metadata_report_multilevel_mapping_saturation):
    response = client.get("/metadata/reports/")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert (
        metadata_report_multilevel_mapping_saturation["multilevel-mapping-saturation"]
        == result["multilevel-mapping-saturation"]
    )
    assert "minimal" not in result.keys()


def test_by_key(client, response_template, metadata_report_minimal):
    response = client.get("/metadata/reports/minimal")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_report_minimal


def test_by_key_not_found_error(client):
    response = client.get("/metadata/reports/foo")
    assert response.status_code == 422


def test_project_core(
    client, response_template, metadata_report_multilevel_mapping_saturation
):
    response = client.get("/metadata/reports/?project=core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert (
        metadata_report_multilevel_mapping_saturation["multilevel-mapping-saturation"]
        == result["multilevel-mapping-saturation"]
    )
    assert "minimal" not in result.keys()


def test_project_all(
    client,
    response_template,
):
    response = client.get("/metadata/reports/?project=all")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert len(result) == len(ReportEnum)


def test_project_not_found_error(client):
    response = client.get("/metadata/reports/?project=foo")
    assert response.status_code == 422
