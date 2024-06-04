"""Pydantic Models for Projects."""

from pydantic import BaseModel, ConfigDict


class Project(BaseModel):
    name: str
    description: str
    model_config = ConfigDict(
        title="Project",
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )
