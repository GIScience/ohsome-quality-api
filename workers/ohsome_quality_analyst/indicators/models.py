from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Literal, Optional


@dataclass
class Metadata:
    """Metadata of an indicator as defined in the metadata.yaml file."""

    name: str
    description: str
    label_description: Dict
    result_description: str


@dataclass
class Result:
    """The result of the Indicator.

    Attributes:
        timestamp_oqt (datetime): Timestamp of the creation of the indicator
        timestamp_osm (datetime): Timestamp of the used OSM data
            (e.g. Latest timestamp of the ohsome API results)
        label (str): Traffic lights like quality label: `green`, `yellow` or `red`. The
            value is determined by the result classes
        value (float): The result value
        class_ (int): The result class. An integer between 1 and 5. It maps to the
            result labels. This value is used by the reports to determine an overall
            result.
        description (str): The result description.
        svg (str): Figure of the result as SVG
    """

    description: str
    svg: str
    html: str
    timestamp_oqt: datetime = datetime.now(timezone.utc)  # UTC datetime object
    timestamp_osm: Optional[datetime] = None
    value: Optional[float] = None
    class_: Optional[Literal[1, 2, 3, 4, 5]] = None
    figure: Optional[dict] = None

    @property
    def label(self) -> Literal["green", "yellow", "red", "undefined"]:
        labels = {1: "red", 2: "yellow", 3: "yellow", 4: "green", 5: "green"}
        return labels.get(self.class_, "undefined")
