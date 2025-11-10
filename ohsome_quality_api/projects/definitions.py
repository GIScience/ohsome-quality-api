"""Global Variables and Functions."""

import os
from enum import Enum

import yaml

from ohsome_quality_api.projects.models import Project
from ohsome_quality_api.utils.helper import get_module_dir


def get_project_keys() -> list[str]:
    return [str(t) for t in load_projects().keys()]


def load_projects() -> dict[str, Project]:
    """Read definitions of projects.

    Returns:
        A dict with all projects included.
    """
    directory = get_module_dir("ohsome_quality_api.projects")
    file = os.path.join(directory, "projects.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    projects = {}
    for k, v in raw.items():
        projects[k] = Project(**v)
    return projects


def get_project_metadata() -> dict[str, Project]:
    projects = load_projects()
    return projects


def get_project(project_key: str) -> Project:
    projects = get_project_metadata()
    try:
        return projects[project_key]
    except KeyError as error:
        raise KeyError(
            "Invalid project key. Valid project keys are: " + str(projects.keys())
        ) from error


ProjectEnum = Enum("ProjectEnum", {key: key for key in get_project_keys() + ["all"]})
