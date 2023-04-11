import pytest


def test(client, response_template, metadata_report_minimal):
    response = client.get("/metadata/reports/")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_report_minimal == next(
        filter(lambda r: r["name"] == "Minimal", result)
    )


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


@pytest.mark.skip(reason="Not yet implemented")
def test_project_misc(client, response_template, metadata_report_minimal):
    response = client.get("/metadata/reports/?project=misc")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_report_minimal == next(
        filter(lambda r: r["name"] == "Minimal", result)
    )
    assert "Minimal" not in [r["name"] for r in result]


@pytest.mark.skip(reason="Not yet implemented")
def test_project_not_found_error(client):
    response = client.get("/metadata/reports/?project=foo")
    assert response.status_code == 404  # Not Found
    # content = response.json()
