"""Pydantic Models for Quality Dimensions."""
from pydantic import BaseModel, ConfigDict


class QualityDimension(BaseModel):
    name: str
    description: str
    model_config = ConfigDict(
        title="Topic",
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )
