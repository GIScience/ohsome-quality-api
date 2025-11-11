"""Pydantic Models for Quality Dimensions."""

from fastapi_i18n import _
from pydantic import BaseModel, ConfigDict, field_validator


class QualityDimension(BaseModel):
    name: str
    description: str
    source: str | None = None
    model_config = ConfigDict(
        title="Topic",
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )

    @field_validator("name", "description", mode="before")
    @classmethod
    def translate(cls, value: str) -> str:
        return _(value)
