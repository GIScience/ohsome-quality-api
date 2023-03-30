"""Pydantic Models for Topics

Note:
    The topic key, name, description and the ohsome API endpoint and filter are defined
    in the `presets.yaml` file in the `topic` module.
"""

from typing import Optional

from pydantic import BaseModel


class BaseTopic(BaseModel):
    key: str
    name: str
    description: str

    class Config:
        title = "Topic"
        frozen = True
        extra = "forbid"


class TopicDefinition(BaseTopic):
    """Includes the ohsome API endpoint and parameters needed to retrieve the data."""

    endpoint: str
    filter_: str
    project: str
    source: Optional[str] = None
    ratio_filter: Optional[str] = None


class TopicData(BaseTopic):
    """Includes the data associated with the topic."""

    data: dict
