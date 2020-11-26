import json
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.layers import SKETCHMAP_FITNESS_POI_LAYER


class Indicator(BaseIndicator):
    """The POI Density Indicator."""

    name = "POI_DENSITY"

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = SKETCHMAP_FITNESS_POI_LAYER,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
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

        query_results = ohsome_api.process_ohsome_api(
            endpoint="/elements/count/density/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
        )

        preprocessing_results = {}

        for layer in self.layers.keys():
            preprocessing_results[f"{layer}_density"] = query_results[layer]["result"][
                0
            ]["value"]

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict) -> Dict:
        logger.info(f"run calculation for {self.name} indicator")
        # compute relative densities

        return preprocessing_results

        # TODO: why is this named 'old' keys, let's make this more easy to understand
        """
        old_keys = [
            "park",
            "national_park",
            "waterway",
            "water",
            "pharmacy",
            "hospital",
            "school",
            "college",
            "university",
            "police",
            "fire_station",
            "bus_stop",
            "station",
        ]

        # TODO: why do we compute relative density?
        relative_density_dict = {}
        for k, v in preprocessing_results.items():
            if k not in old_keys and k != "density":
                relative_density_dict[k] = round(
                    100 * v / preprocessing_results["density"], 2
                )
        results = {"relative_poi_densities": relative_density_dict}
        """

    def create_figure(self, results: Dict):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
