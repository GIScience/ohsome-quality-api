from __future__ import annotations  # superfluous in Python 3.10

import logging
from abc import ABCMeta, abstractmethod
from typing import NamedTuple

import numpy as np
from geojson_pydantic import Feature

from ohsome_quality_analyst.definitions import get_attribution, get_metadata
from ohsome_quality_analyst.indicators.base import BaseIndicator
from ohsome_quality_analyst.reports.models import ReportMetadata, Result


class IndicatorTopic(NamedTuple):
    indicator_name: str
    topic_key: str


class BaseReport(metaclass=ABCMeta):
    def __init__(
        self,
        feature: Feature,
        indicator_topic: tuple[IndicatorTopic] = None,
        blocking_red: bool = False,
        blocking_undefined: bool = False,
    ):
        self.metadata: ReportMetadata = get_metadata("reports", type(self).__name__)
        self.feature = feature

        self.indicators: list[BaseIndicator] = []
        self.indicator_topic = indicator_topic  # Defines indicator+topic combinations
        self.blocking_undefined = blocking_undefined
        self.blocking_red = blocking_red
        # Results will be written during the lifecycle of the report object (combine())
        self.result = Result()

    def as_feature(self, include_data: bool = False) -> Feature:
        """Returns a GeoJSON Feature object.

        The properties of the Feature contains the attributes of all indicators.
        The geometry (and properties) of the input GeoJSON object is preserved.
        """
        result = self.result.dict(by_alias=True)  # only attributes, no properties
        result["label"] = self.result.label  # label is a property
        properties = {
            "report": {
                "metadata": self.metadata.dict(),
                "result": result,
            },
            "indicators": [],
        }
        properties["report"]["metadata"].pop("label_description", None)

        for i, indicator in enumerate(self.indicators):
            properties["indicators"].append(
                indicator.as_feature(include_data=include_data).properties
            )
        if self.feature.id is not None:
            return Feature(
                type="Feature",
                id=self.feature.id,
                geometry=self.feature.geometry,
                properties=properties,
            )
        else:
            return Feature(
                type="Feature", geometry=self.feature.geometry, properties=properties
            )

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
