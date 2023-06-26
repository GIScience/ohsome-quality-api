"""Pydantic Models for Topics

Note:
    The topic key, name, description and the ohsome API endpoint and filter are defined
    in the `presets.yaml` file in the `topic` module.
"""

from typing import List, Optional

from pydantic import BaseModel

from ohsome_quality_analyst.projects.definitions import ProjectEnum
from ohsome_quality_analyst.utils.helper import snake_to_hyphen


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
    filter: str
    indicators: List[str]
    projects: list[ProjectEnum]
    source: Optional[str] = None
    ratio_filter: Optional[str] = None

    class Config:
        alias_generator = snake_to_hyphen
        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True


class TopicData(BaseTopic):
    """Includes the data associated with the topic."""

    data: dict
