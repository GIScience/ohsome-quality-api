import pytest
from pydantic import ValidationError

from ohsome_quality_analyst.projects.models import Project


def test_project():
    Project(name="My fancy Project", description="some description")


def test_parameter_missing():
    with pytest.raises(ValidationError):
        Project(name="some name")
    with pytest.raises(ValidationError):
        Project(description="description")


def test_extra_parameter():
    with pytest.raises(ValidationError):
        Project(
            name="My fancy Project",
            description="some description",
            foo="bar",
        )
