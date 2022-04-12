import logging
import os
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from statistics import mean
from typing import Dict, List, Literal, NamedTuple, Tuple

from dacite import from_dict
from geojson import Feature
from jinja2 import Environment, FileSystemLoader

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.utils.definitions import get_attribution, get_metadata
from ohsome_quality_analyst.utils.helper import flatten_dict


@dataclass
class Metadata:
    """Metadata of a report as defined in the metadata.yaml file"""

    name: str
    description: str
    label_description: Dict


@dataclass
class Result:
    """The result of the Report."""

    label: Literal["green", "yellow", "red", "undefined"]
    value: float
    description: str
    html: str


class IndicatorLayer(NamedTuple):
    indicator_name: str
    layer_name: str


class BaseReport(metaclass=ABCMeta):
    """Subclass has to create and append indicator objects to indicators list."""

    def __init__(self, feature: Feature = None):
        self.feature = feature

        # Defines indicator+layer combinations
        self.indicator_layer: Tuple[IndicatorLayer] = []
        self.indicators: List[BaseIndicator] = []

        metadata = get_metadata("reports", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)
        # Results will be written during the lifecycle of the report object (combine())
        self.result = Result(None, None, None, None)

    def as_feature(self) -> Feature:
        """Returns a GeoJSON Feature object.

        The properties of the Feature contains the attributes of all indicators.
        The geometry (and properties) of the input GeoJSON object is preserved.
        """
        report_properties = {
            "metadata": vars(self.metadata).copy(),
            "result": vars(self.result).copy(),
        }
        report_properties["metadata"].pop("label_description", None)
        properties = flatten_dict(report_properties, prefix="report")
        for i, indicator in enumerate(self.indicators):
            p = indicator.as_feature(flatten=True)["properties"]
            properties.update(
                {"indicators." + str(i) + "." + str(key): val for key, val in p.items()}
            )
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

        values = []
        for indicator in self.indicators:
            if indicator.result.label != "undefined":
                values.append(indicator.result.value)
        if not values:
            self.result.value = None
            self.result.label = "undefined"
            self.result.description = "Could not derive quality level"
            return None
        else:
            self.result.value = mean(values)

        if self.result.value < 0.5:
            self.result.label = "red"
            self.result.description = self.metadata.label_description["red"]
        elif self.result.value < 1:
            self.result.label = "yellow"
            self.result.description = self.metadata.label_description["yellow"]
        elif self.result.value >= 1:
            self.result.label = "green"
            self.result.description = self.metadata.label_description["green"]

    @abstractmethod
    def set_indicator_layer(self) -> None:
        """Set the attribute indicator_layer."""
        pass

    @classmethod
    def attribution(cls) -> str:
        """Data attribution as text.

        Defaults to OpenStreetMap attribution.

        This property should be overwritten by the Sub Class if additional data
        attribution is necessary.
        """
        return get_attribution(["OSM"])

    def create_html(self):
        template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
        )
        env = Environment(loader=FileSystemLoader(template_dir))

        template = env.get_template("report_template.html")

        def traffic_light(label, red="#bbb", yellow="#bbb", green="#bbb"):
            dot_css = (
                "style='height: 25px; width: 25px; background-color: {0};"
                "border-radius: 50%; display: inline-block;'"
            )
            return (
                "<span {0} class='dot'></span>\n<span {1} class='dot'>"
                "</span>\n<span {2} class='dot'></span>\n {3}".format(
                    dot_css.format(red),
                    dot_css.format(yellow),
                    dot_css.format(green),
                    label,
                )
            )

        if self.result.label == "red":
            traffic_light = traffic_light("Bad Quality", red="#FF0000")
        elif self.result.label == "yellow":
            traffic_light = traffic_light("Medium Quality", yellow="#FFFF00")
        elif self.result.label == "green":
            traffic_light = traffic_light("Good Quality", green="#008000")
        else:
            traffic_light = traffic_light("Undefined Quality")

        self.result.html = template.render(
            report_name=self.metadata.name,
            indicators="".join([i.result.html for i in self.indicators]),
            result_description=self.result.description,
            metadata=self.metadata.description,
            traffic_light=traffic_light,
        )
