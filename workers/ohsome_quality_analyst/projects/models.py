"""Pydantic Models for Projects."""
from pydantic import BaseModel


class Project(BaseModel):
    name: str
    description: str

    class Config:
        title = "Project"
        frozen = True
        extra = "forbid"
