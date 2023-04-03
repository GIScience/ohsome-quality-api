from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class Metadata:
    """Metadata of a report as defined in the metadata.yaml file"""

    name: str
    description: str
    label_description: dict


@dataclass
class Result:
    """The result of the Report."""

    class_: Literal[1, 2, 3, 4, 5] | None = None
    description: str = ""
    html: str = ""

    @property
    def label(self) -> Literal["green", "yellow", "red", "undefined"]:
        labels = {1: "red", 2: "yellow", 3: "yellow", 4: "green", 5: "green"}
        return labels.get(self.class_, "undefined")
