from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseLayer:
    name: str
    description: str


@dataclass
class LayerDefinition(BaseLayer):
    """Layer class including the ohsome API parameters needed to retrieve the data.

    Note:
        The layer name, description and ohsome API parameters are defined in the
        `layer_definitions.yaml` file.
    """

    key: str
    endpoint: str
    filter_: str
    project: str
    source: Optional[str] = None
    ratio_filter: Optional[str] = None


@dataclass
class LayerData(BaseLayer):
    """Layer class including the data associated with the layer."""

    data: dict
    key: Optional[str] = None

    def __post_init__(self):
        if self.key is None:
            self.key = self.name.replace(" ", "_").lower()
