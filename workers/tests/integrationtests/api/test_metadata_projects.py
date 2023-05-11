def test_metadata_projects(client, response_template, metadata_project_core):
    response = client.get("/metadata/projects")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert metadata_project_core["core"] == result["core"]


def test_metadata_projects_by_key(client, response_template, metadata_project_core):
    response = client.get("/metadata/projects/core")
    assert response.status_code == 200

    content = response.json()
    result = content.pop("result")
    assert content == response_template
    assert result == metadata_project_core


def test_metadata_projects_by_key_not_found_error(client):
    response = client.get("/metadata/projects/foo")
    assert response.status_code == 422
