from typing import Literal

from pydantic import BaseModel, ConfigDict

from ohsome_quality_analyst.projects.definitions import ProjectEnum
from ohsome_quality_analyst.utils.helper import snake_to_lower_camel


class ReportMetadata(BaseModel):
    """Metadata of a report as defined in the metadata.yaml file"""

    name: str
    description: str
    label_description: dict
    projects: list[ProjectEnum]
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        title="Metadata",
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )


class Result(BaseModel):
    """The result of the Report."""

    class_: Literal[1, 2, 3, 4, 5] | None = None
    description: str = ""
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        extra="forbid",
        populate_by_name=True,
    )

    @property
    def label(self) -> Literal["green", "yellow", "red", "undefined"]:
        labels = {1: "red", 2: "yellow", 3: "yellow", 4: "green", 5: "green"}
        return labels.get(self.class_, "undefined")
