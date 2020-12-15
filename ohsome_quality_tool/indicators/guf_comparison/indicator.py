import json
import os
from math import ceil
from typing import Dict, Tuple

import pygal
from geojson import FeatureCollection
from pygal.style import Style

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

    def preprocess(self) -> Dict:
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
            guf_built_up_area = result[0][0]

            # Get total area in square meter of AOI
            sql_file = os.path.join(directory, "get_area.sql")
            with open(sql_file) as reader:
                query = reader.read()
            result = db.retr_query(query=query, data=(aoi_geom,))
            area = result[0][0]
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
        osm_built_up_area = query_results["buildings"]["result"][0]["value"]

        return {
            "guf_built_up_area": guf_built_up_area,
            "osm_built_up_area": osm_built_up_area,
            "area": area,
        }

    def calculate(
        self, preprocessing_results: Dict
    ) -> Tuple[TrafficLightQualityLevels, float, str, Dict]:

        ratio = (
            preprocessing_results["osm_built_up_area"]
            / preprocessing_results["guf_built_up_area"]
        )
        # TODO: Determine right thresholds
        green_threshold = 0.6
        yellow_threshold = 0.2

        if ratio <= yellow_threshold:
            value = TrafficLightQualityLevels.RED.value
        elif ratio <= green_threshold:
            value = TrafficLightQualityLevels.YELLOW.value
        else:
            value = TrafficLightQualityLevels.GREEN.value

        label = TrafficLightQualityLevels(ceil(value))
        text = "test test test"

        return label, value, text, preprocessing_results

    def create_figure(self, data: Dict) -> str:
        # TODO: maybe not all indicators will export figures?
        green_threshold = 0.6
        yellow_threshold = 0.2
        CustomStyle = Style(colors=("green", "yellow", "blue"))
        xy_chart = pygal.XY(stroke=True, style=CustomStyle)

        xy_chart.add("test", ((0, 0), (data["area"], green_threshold * data["area"])))
        xy_chart.add("test2", ((0, 0), (data["area"], yellow_threshold * data["area"])))

        xy_chart.add("test2", ((data["guf_built_up_area"], data["osm_built_up_area"])))

        xy_chart.title = "POI Density (POIs per Area)"
        xy_chart.x_title = "GUF"
        xy_chart.y_title = "OSM"

        figure = xy_chart.render(is_unicode=True)
        xy_chart.render_to_png("/tmp/chart.png")
        logger.info(f"export figures for {self.name} indicator")
