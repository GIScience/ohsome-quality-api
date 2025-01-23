"""Pydantic Models for Attributes."""

from pydantic import BaseModel, ConfigDict


class Attribute(BaseModel):
    filter: str
    name: str
    description: str
    filter_sql: str | None = None  # TODO: Should not be optional
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        title="Attribute",
    )
