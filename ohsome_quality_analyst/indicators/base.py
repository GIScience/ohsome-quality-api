import glob
import json
from abc import ABCMeta, abstractmethod

import plotly.graph_objects as go
import yaml
from geojson import Feature

from ohsome_quality_analyst.definitions import get_attribution
from ohsome_quality_analyst.indicators.models import IndicatorMetadata, Result
from ohsome_quality_analyst.topics.models import BaseTopic as Topic
from ohsome_quality_analyst.utils.helper import (
    camel_to_hyphen,
    camel_to_snake,
    get_module_dir,
    json_serialize,
)


class BaseIndicator(metaclass=ABCMeta):
    """The base class of every indicator."""

    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        self.metadata: IndicatorMetadata = self.get_template()
        self.topic: Topic = topic
        self.feature: Feature = feature
        self.result: Result = Result(
            description=self.metadata.label_description["undefined"],
        )
        self._get_default_figure()

    def as_dict(self, include_data: bool = False, exclude_label: bool = False) -> dict:
        if exclude_label:
            result = self.result.model_dump(by_alias=True, exclude={"label"})
        else:
            result = self.result.model_dump(by_alias=True)
        raw_dict = {
            "metadata": self.metadata.model_dump(
                by_alias=True,
                exclude={"result_description", "label_description"},
            ),
            "topic": self.topic.model_dump(
                by_alias=True,
                exclude={"ratio_filter"},
            ),
            "result": result,
            **self.feature.properties,
        }
        if include_data:
            raw_dict["data"] = self.data
        if "id" in self.feature.keys():
            raw_dict["id"] = self.feature.id
        return raw_dict

    def as_feature(self, include_data: bool = False, exclude_label=False) -> Feature:
        """Return a GeoJSON Feature object.

        The properties of the Feature contains the attributes of the indicator.
        The geometry (and properties) of the input GeoJSON object is preserved.

        Args:
            include_data (bool): If true include additional data in the properties.
        """
        properties = self.as_dict(include_data, exclude_label)
        if "id" in self.feature.keys():
            return Feature(
                id=self.feature.id,
                geometry=self.feature.geometry,
                properties=properties,
            )
        else:
            return Feature(
                geometry=self.feature.geometry,
                properties=properties,
            )

    @property
    def data(self) -> dict:
        """All Indicator object attributes except feature, result, metadata and topic.

        Note:
            Attributes will be dumped and immediately loaded again by the `json`
            library. In this process a custom function for serializing data types which
            are not supported by the `json` library (E.g. numpy datatypes or objects of
            the `BaseModelStats` class) will be executed.
        """
        data = vars(self).copy()
        data.pop("result")
        data.pop("metadata")
        data.pop("topic")
        data.pop("feature")
        return json.loads(json.dumps(data, default=json_serialize).encode())

    @classmethod
    def attribution(cls) -> str:
        """Return data attribution as text.

        Defaults to OpenStreetMap attribution.

        This property should be overwritten by the Sub Class if additional data
        attribution is necessary.
        """
        return get_attribution(["OSM"])

    @abstractmethod
    async def preprocess(self) -> None:
        """Get fetch and preprocess data.

        Fetch data from the ohsome API and/or from the geodatabase asynchronously.
        Preprocess data for calculation and save those as attributes.
        """
        pass

    @abstractmethod
    def calculate(self) -> None:
        """Calculate indicator results.

        Writes the results to the result attribute.
        """
        pass

    @abstractmethod
    def create_figure(self) -> None:
        pass

    def _get_default_figure(self) -> None:
        fig = go.Figure()
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        # add text annotation at the center
        fig.add_annotation(
            text="The creation of the Indicator was unsuccessful.",
            showarrow=False,
            font=dict(size=32, color="black"),
        )

        fig.update_xaxes(showticklabels=False, zeroline=False)
        fig.update_yaxes(showticklabels=False, zeroline=False)

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def get_template(self) -> None:
        """Get template for indicator."""
        indicator_key = camel_to_snake(type(self).__name__)
        directory = get_module_dir(
            "ohsome_quality_analyst.indicators.{}".format(indicator_key)
        )
        file = glob.glob(directory + "/metadata.yaml", recursive=True)
        with open(file[0], "r") as file:
            raw = yaml.safe_load(file)
        metadata = {}
        for k, v in raw.items():
            metadata[k] = IndicatorMetadata(**v)
        return metadata[camel_to_hyphen(type(self).__name__)]
