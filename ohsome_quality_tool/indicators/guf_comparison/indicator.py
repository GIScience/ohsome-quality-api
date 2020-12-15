import io
import json
import os
from math import ceil
from typing import Dict, Tuple

import matplotlib.pyplot as plt
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import geodatabase, ohsome_api
from ohsome_quality_tool.utils.auth import PostgresDB
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Indicator(BaseIndicator):
    """Set number of features and population into perspective."""

    name = "guf-comparison"
    description = (
        "Compare OSM features against built up area defined by "
        "Global Urban Footprint dataset."
    )

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = LEVEL_ONE_LAYERS,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: str = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layers=layers,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        # TODO: Change arbitrary thresholds
        self.threshold_high: float = 0.6
        self.threshold_low: float = 0.2
        self.area: float = None
        self.guf_built_up_area: float = None
        self.osm_built_up_area: float = None

    def preprocess(self) -> None:
        logger.info(f"run preprocessing for {self.name} indicator")
        db = PostgresDB()

        if self.dynamic:
            directory = os.path.dirname(os.path.abspath(__file__))
            aoi_geom = json.dumps(self.bpolys["features"][0]["geometry"])

            # Get built-up area in square meter of GUF04 for AOI
            sql_file = os.path.join(directory, "get_built_up_area.sql")
            with open(sql_file) as reader:
                query = reader.read()
            result = db.retr_query(query=query, data=(aoi_geom, aoi_geom))
            self.guf_built_up_area = result[0][0]

            # Get total area in square meter of AOI
            sql_file = os.path.join(directory, "get_area.sql")
            with open(sql_file) as reader:
                query = reader.read()
            result = db.retr_query(query=query, data=(aoi_geom,))
            self.area = result[0][0]
        else:
            built_up_area = geodatabase.get_value_from_db(
                dataset=self.dataset,
                feature_id=self.feature_id,
                field_name="population",
            )

        # TODO: Difficult to read and understand.
        self.layers = {"buildings": {"filter": "building=*", "unit": "area"}}
        query_results = ohsome_api.process_ohsome_api(
            endpoint="elements/{unit}/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )
        self.osm_built_up_area = query_results["buildings"]["result"][0]["value"]

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:

        ratio = self.guf_built_up_area / self.osm_built_up_area

        if ratio <= self.threshold_low:
            value = TrafficLightQualityLevels.RED.value
        elif ratio <= self.threshold_high:
            value = TrafficLightQualityLevels.YELLOW.value
        else:
            value = TrafficLightQualityLevels.GREEN.value

        label = TrafficLightQualityLevels(ceil(value))
        text = "test test test"

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        fig = plt.figure()
        ax = fig.add_subplot()

        # Plot thresholds as line.
        ax.plot(
            [0, self.area],
            [0, self.area * self.threshold_high],
            color="black",
            label="Threshold",
        )
        ax.plot(
            [0, self.area],
            [0, self.area * self.threshold_low],
            color="black",
            label="Threshold",
        )

        # Plot point as circle ("o").
        ax.plot(
            self.guf_built_up_area,
            self.osm_built_up_area,
            "o",
            color="black",
            label="Indicator value: {0}/{1}".format(
                self.guf_built_up_area, self.osm_built_up_area
            ),
        )

        ax.set_ylabel("Open Street Map")  # Add a y-label to the axes.
        ax.set_title("Built-Up Area")  # Add a title to the axes.
        ax.legend()  # Add a legend.

        # Save as SVG to file-like object and return as string.
        output_file = io.BytesIO()
        plt.savefig("test.svg", format="svg")
        logger.info(f"export figures for {self.name} indicator")
        return output_file.getvalue()
