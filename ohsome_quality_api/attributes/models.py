"""Pydantic Models for Attributes."""

from fastapi_i18n import _
from pydantic import BaseModel, ConfigDict, field_validator


class Attribute(BaseModel):
    filter: str
    name: str
    description: str
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        title="Attribute",
    )

    @field_validator("name", "description", mode="before")
    @classmethod
    def translate(cls, value: str) -> str:
        return _(value)
