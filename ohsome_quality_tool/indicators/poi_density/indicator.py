import json
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """The POI Density Indicator."""

    name = "POI Density"

    def __init__(
        self,
        dynamic: bool,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic, bpolys=bpolys, dataset=dataset, feature_id=feature_id
        )

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        # category name as key, filter string as value
        categories = {
            "mountain": "natural=peak",
            "gas_stations": "amenity=fuel",
            "parks": "leisure=park or boundary=national_park",
            "waterways": "natural=water or waterway=*",
            "health_fac_pharmacies": "amenity in (pharmacy, hospital)",
            "eduction": "amenity in (school, college, university)",
            "public_safety": "amenity in (police, fire_station)",
            "public_transport": "highway=bus_stop or railway=station",
            "hotel": "tourism=hotel",
            "attraction": "tourism=attraction",
            "restaurant": "amenity=restaurant",
            "townhall": "amenity=townhall",
            "shop": "shop=*",
        }

        preprocessing_results = ohsome_api.query_ohsome_api(
            endpoint="/elements/count/density/",
            categories=categories,
            bpolys=json.dumps(self.bpolys),
        )

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

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
