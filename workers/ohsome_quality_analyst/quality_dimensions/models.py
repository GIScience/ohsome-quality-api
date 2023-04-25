"""Pydantic Models for Quality Dimensions

Note:
    TODO The topic key, name, description and the ohsome API endpoint and filter are
    defined in the `quality_dimensions.yaml` file in the `quality_dimensions` module.
"""
from pydantic import BaseModel


class QualityDimension(BaseModel):
    name: str
    description: str

    class Config:
        title = "Topic"
        frozen = True
        extra = "forbid"
