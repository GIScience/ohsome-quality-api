from typing import Literal

from pydantic import BaseModel

from ohsome_quality_analyst.projects.definitions import ProjectEnum
from ohsome_quality_analyst.utils.helper import snake_to_lower_camel


class ReportMetadata(BaseModel):
    """Metadata of a report as defined in the metadata.yaml file"""

    name: str
    description: str
    label_description: dict
    projects: list[ProjectEnum]

    class Config:
        alias_generator = snake_to_lower_camel
        title = "Metadata"
        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True


class Result(BaseModel):
    """The result of the Report."""

    class_: Literal[1, 2, 3, 4, 5] | None = None
    description: str = ""

    class Config:
        alias_generator = snake_to_lower_camel
        extra = "forbid"
        allow_population_by_field_name = True

    @property
    def label(self) -> Literal["green", "yellow", "red", "undefined"]:
        labels = {1: "red", 2: "yellow", 3: "yellow", 4: "green", 5: "green"}
        return labels.get(self.class_, "undefined")
