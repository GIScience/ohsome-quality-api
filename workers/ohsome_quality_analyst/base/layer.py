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

    endpoint: str
    filter_: str
    source: Optional[str] = None
    ratio_filter: Optional[str] = None


@dataclass
class LayerData(BaseLayer):
    """Layer class including the data associated with the layer."""

    data: dict
