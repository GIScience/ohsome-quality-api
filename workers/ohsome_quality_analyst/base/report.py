from __future__ import annotations  # superfluous in Python 3.10

import logging
from abc import ABCMeta, abstractmethod
from dataclasses import asdict, dataclass
from typing import List, Literal, NamedTuple, Tuple

import numpy as np
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.definitions import get_attribution, get_metadata
from ohsome_quality_analyst.html_templates.template import (
    get_template,
    get_traffic_light,
)
from ohsome_quality_analyst.utils.helper import flatten_dict


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


class IndicatorLayer(NamedTuple):
    indicator_name: str
    layer_key: str


class BaseReport(metaclass=ABCMeta):
    def __init__(
        self,
        feature: Feature,
        indicator_layer: Tuple[IndicatorLayer] = None,
        blocking_red: bool = False,
        blocking_undefined: bool = False,
    ):
        self.feature = feature

        self.indicators: List[BaseIndicator] = []
        metadata = get_metadata("reports", type(self).__name__)
        self.indicator_layer = indicator_layer  # Defines indicator+layer combinations
        self.blocking_undefined = blocking_undefined
        self.blocking_red = blocking_red
        self.metadata: Metadata = Metadata(
            name=metadata["name"],
            description=metadata["description"],
            label_description=metadata["label-description"],
        )
        # Results will be written during the lifecycle of the report object (combine())
        self.result = Result()

    def as_feature(self, flatten: bool = False, include_data: bool = False) -> Feature:
        """Returns a GeoJSON Feature object.

        The properties of the Feature contains the attributes of all indicators.
        The geometry (and properties) of the input GeoJSON object is preserved.
        """
        result = asdict(self.result)  # only attributes, no properties
        result["label"] = self.result.label  # label is a property
        if result["class_"] is not None:
            result["class_"] = self.result.class_
        properties = {
            "report": {
                "metadata": asdict(self.metadata),
                "result": result,
            },
            "indicators": [],
        }
        properties["report"]["metadata"].pop("label_description", None)

        for i, indicator in enumerate(self.indicators):
            properties["indicators"].append(
                indicator.as_feature(include_data=include_data)["properties"]
            )
        if flatten:
            properties = flatten_dict(properties)
        if "id" in self.feature.keys():
            return Feature(
                id=self.feature.id,
                geometry=self.feature.geometry,
                properties=properties,
            )
        else:
            return Feature(geometry=self.feature.geometry, properties=properties)

    @abstractmethod
    def combine_indicators(self) -> None:
        """Combine indicators results and create the report result object."""
        logging.info(f"Combine indicators for report: {self.metadata.name}")

        if self.blocking_undefined:
            if any(i.result.class_ is None for i in self.indicators):
                self.result.class_ = None
                self.result.description = self.metadata.label_description["undefined"]
                return

        if self.blocking_red:
            if any(i.result.class_ == 1 for i in self.indicators):
                self.result.class_ = 1
                self.result.description = self.metadata.label_description["red"]
                return

        if all(i.result.class_ is None for i in self.indicators):
            self.result.class_ = None
            self.result.description = self.metadata.label_description["undefined"]
        else:
            self.result.class_ = round(
                np.mean(
                    [
                        i.result.class_
                        for i in self.indicators
                        if i.result.class_ is not None
                    ]
                )
            )

        if self.result.class_ in (4, 5):
            self.result.description = self.metadata.label_description["green"]
        elif self.result.class_ in (2, 3):
            self.result.description = self.metadata.label_description["yellow"]
        elif self.result.class_ == 1:
            self.result.description = self.metadata.label_description["red"]
        else:
            self.result.description = self.metadata.label_description["undefined"]

    @classmethod
    def attribution(cls) -> str:
        """Data attribution as text.

        Defaults to OpenStreetMap attribution.

        This property should be overwritten by the Sub Class if additional data
        attribution is necessary.
        """
        return get_attribution(["OSM"])

    def create_html(self):
        if self.result.label == "red":
            traffic_light = get_traffic_light("Bad Quality", red="#FF0000")
        elif self.result.label == "yellow":
            traffic_light = get_traffic_light("Medium Quality", yellow="#FFFF00")
        elif self.result.label == "green":
            traffic_light = get_traffic_light("Good Quality", green="#008000")
        else:
            traffic_light = get_traffic_light("Undefined Quality")
        template = get_template("report")
        self.result.html = template.render(
            report_name=self.metadata.name,
            indicators="".join([i.result.html for i in self.indicators]),
            result_description=self.result.description,
            metadata=self.metadata.description,
            traffic_light=traffic_light,
        )
