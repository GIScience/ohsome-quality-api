"""Pydantic Models for Quality Dimensions."""
from pydantic import BaseModel


class QualityDimension(BaseModel):
    name: str
    description: str

    class Config:
        title = "Topic"
        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
