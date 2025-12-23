"""Pydantic Models for Quality Dimensions."""

from pydantic import BaseModel, ConfigDict


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
