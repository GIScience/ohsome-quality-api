"""Pydantic Models for Projects."""

from fastapi_i18n import _
from pydantic import BaseModel, ConfigDict, field_validator


class Project(BaseModel):
    name: str
    description: str
    model_config = ConfigDict(
        title="Project",
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )

    @field_validator("name", "description", mode="before")
    @classmethod
    def translate(cls, value: str) -> str:
        return _(value)
