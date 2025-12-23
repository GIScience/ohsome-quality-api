"""Pydantic Models for Attributes."""

from pydantic import BaseModel, ConfigDict


class Attribute(BaseModel):
    filter: str
    name: str
    description: str
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        title="Attribute",
    )
