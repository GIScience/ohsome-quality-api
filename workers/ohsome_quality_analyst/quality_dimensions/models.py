"""Pydantic Models for Quality Dimensions."""
from pydantic import BaseModel


class QualityDimension(BaseModel):
    name: str
    description: str

    class Config:
        title = "Topic"
        frozen = True
        extra = "forbid"
