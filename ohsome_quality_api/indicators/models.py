from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from ohsome_quality_api.projects.definitions import ProjectEnum
from ohsome_quality_api.quality_dimensions.definitions import QualityDimensionEnum
from ohsome_quality_api.utils.helper import snake_to_lower_camel


class IndicatorMetadata(BaseModel):
    """Metadata of an indicator as defined in the metadata.yaml file."""

    name: str
    description: str
    projects: list[ProjectEnum]
    quality_dimension: QualityDimensionEnum
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        title="Metadata",
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )


class IndicatorTemplates(BaseModel):
    """Result text templates of an indicator as defined in the templates.yaml file."""

    label_description: dict[str, str]
    result_description: str


class Result(BaseModel):
    """The result of the Indicator.

    Attributes:
        timestamp (datetime): Timestamp of the creation of the indicator
        timestamp_osm (datetime): Timestamp of the used OSM data
            (e.g. Latest timestamp of the ohsome API results)
        label (str): Traffic lights like quality label: `green`, `yellow` or `red`. The
            value is determined by the result classes
        value (float): The result value
        class_ (int): The result class. An integer between 1 and 5. It maps to the
            result labels. This value is used by the reports to determine an overall
            result.
        description (str): The result description.
    """

    description: str
    timestamp: datetime = Field(default=datetime.now(timezone.utc))
    timestamp_osm: datetime | None = Field(default=None, alias="timestampOSM")
    value: float | None = None
    class_: Literal[1, 2, 3, 4, 5] | None = None
    figure: dict | None = None
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        extra="forbid",
        populate_by_name=True,
    )

    @computed_field
    @property
    def label(self) -> Literal["green", "yellow", "red", "undefined"]:
        labels = {1: "red", 2: "yellow", 3: "yellow", 4: "green", 5: "green"}
        return labels.get(self.class_, "undefined")
