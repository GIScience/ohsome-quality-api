import pytest

from ohsome_quality_api.projects import definitions
from ohsome_quality_api.projects.models import Project


@pytest.fixture(params=["misc", "core", "experimental"])
def valid_project_keys(request):
    return request.param


def test_get_projects():
    qds = definitions.get_project_metadata()
    assert isinstance(qds, dict)
    for key, qd in qds.items():
        assert isinstance(key, str)
        assert isinstance(qd, Project)


def test_get_project(valid_project_keys):
    qd = definitions.get_project(valid_project_keys)
    assert isinstance(qd, Project)


def test_get_project_wrong_key():
    with pytest.raises(KeyError):
        definitions.get_project("foo")


def test_get_project_keys_type():
    keys = definitions.get_project_keys()
    assert isinstance(keys, list)
    for key in keys:
        assert isinstance(key, str)


def test_get_project_keys_valid(valid_project_keys):
    keys = definitions.get_project_keys()
    assert valid_project_keys in keys
