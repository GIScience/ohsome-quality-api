"""Pydantic Models for Projects

Note:
    TODO The topic key, name, description and the ohsome API endpoint and filter are
    defined in the `projects.yaml` file in the `projects` module.
"""
from pydantic import BaseModel


class Project(BaseModel):
    name: str
    description: str

    class Config:
        title = "Project"
        frozen = True
        extra = "forbid"
