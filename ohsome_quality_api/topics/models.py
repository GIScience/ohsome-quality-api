"""Pydantic Models for Topics

Note:
    The topic key, name, description and the ohsome API endpoint and filter are defined
    in the `presets.yaml` file in the `topic` module.
"""

from typing import Literal

from fastapi_i18n import _
from pydantic import BaseModel, ConfigDict, field_validator

from ohsome_quality_api.projects.definitions import ProjectEnum
from ohsome_quality_api.utils.helper import snake_to_lower_camel


class BaseTopic(BaseModel):
    key: str
    name: str
    description: str
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        title="Topic",
    )

    @field_validator("name", "description", mode="before")
    @classmethod
    def translate(cls, value: str) -> str:
        return _(value)


class Topic(BaseTopic):
    """Includes the ohsome API endpoint and parameters needed to retrieve the data."""

    endpoint: Literal["elements"]
    aggregation_type: Literal["area", "count", "length", "perimeter", "area/density"]
    filter: str
    indicators: list[str]
    projects: list[ProjectEnum]
    source: str | None = None
    ratio_filter: str | None = None


class TopicData(BaseTopic):
    """Includes the data associated with the topic."""

    data: dict
