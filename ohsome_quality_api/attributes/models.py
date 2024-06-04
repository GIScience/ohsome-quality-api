"""Pydantic Models for Attributes."""

from pydantic import BaseModel


class Attribute(BaseModel):
    filter: str
    name: str
    description: str

    class Config:
        title = "Attribute"
        frozen = True
        extra = "forbid"
