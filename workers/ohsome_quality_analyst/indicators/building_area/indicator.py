import logging
import os

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
from geojson import Feature

from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.ohsome import client as ohsome_client
from ohsome_quality_analyst.utils.helper import load_sklearn_model


class BuildingArea(BaseIndicator):
    """Building Area Indicator

    TODO: Describe model

    Args:
        layer_name (str): Layer name has to reference a building area Layer.
            Unit is in meter.
        feature (Feature): GeoJSON Feature object

    """

    def __init__(
        self,
        layer_name: str,
        feature: Feature,
    ) -> None:
        super().__init__(
            layer_name=layer_name,
            feature=feature,
        )
        self.model_name = ""
        self.building_area = None

    async def preprocess(self) -> None:
        query_results = await ohsome_client.query(
            layer=self.layer, bpolys=self.feature.geometry
        )
        self.building_area = query_results["result"][0]["value"]
        timestamp = query_results["result"][0]["timestamp"]
        self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        # TODO: Use rasterstats to retrive data from raster files (Waiting for PR 227)

    def calculate(self) -> None:
        directory = os.path.dirname(os.path.abspath(__file__))
        scaler = load_sklearn_model(os.path.join(directory, "scaler.joblib"))
        model = load_sklearn_model(os.path.join(directory, "model.joblib"))
        y = model.predict(self.building_area)

    def create_figure(self) -> None:
        raise NotImplementedError
