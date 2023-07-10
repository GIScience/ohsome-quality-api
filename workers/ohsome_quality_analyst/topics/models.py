"""Pydantic Models for Topics

Note:
    The topic key, name, description and the ohsome API endpoint and filter are defined
    in the `presets.yaml` file in the `topic` module.
"""


from pydantic import BaseModel

from ohsome_quality_analyst.projects.definitions import ProjectEnum
from ohsome_quality_analyst.utils.helper import snake_to_lower_camel


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
    indicators: list[str]
    projects: list[ProjectEnum]
    source: str | None = None
    ratio_filter: str | None = None

    class Config:
        alias_generator = snake_to_lower_camel
        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True


class TopicData(BaseTopic):
    """Includes the data associated with the topic."""

    data: dict
