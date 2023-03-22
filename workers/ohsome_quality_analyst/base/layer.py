"""Pydantic Models for Topics

Note:
    The layer key, name, description and the ohsome API endpoint and filter are defined
    in the `layer_definitions.yaml` file in the `ohsome` module.
"""

from typing import Optional

from pydantic import BaseModel


class BaseLayer(BaseModel):
    key: str
    name: str
    description: str

    class Config:
        title = "Topic"
        frozen = True
        extra = "forbid"


class LayerDefinition(BaseLayer):
    """Includes the ohsome API endpoint and parameters needed to retrieve the data."""

    endpoint: str
    filter_: str
    project: str
    source: Optional[str] = None
    ratio_filter: Optional[str] = None


class LayerData(BaseLayer):
    """Includes the data associated with the layer."""

    data: dict
