import json

import requests
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
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
        ohsome_api: str = None,
        density_per_category: dict = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic, bpolys=bpolys, dataset=dataset, feature_id=feature_id
        )

    def preprocess(self):
        logger.info(f"run preprocessing for {self.name} indicator")

        key_multiple_values_filters = {
            "tourism": "hotel,attraction",
            "natural": "water,peak",
            "amenity": "place_of_worship,pharmacy,hospital,restaurant,fuel,townhall,school,university,college,police,fire_station",  # noqa
        }

        key_value_filters = {
            "highway": "bus_stop",
            "railway": "station",
            "leisure": "park",
            "boundary": "national_park",
        }

        key_filters = ["shop", "waterway"]

        density_dict = {"density": 0}  # result dictionary with category counts

        # query ohsome for keys with multiple values
        for k, v in key_multiple_values_filters.items():
            url = "/elements/count/density/groupBy/tag"
            values_separate = v.split(",")
            params = {
                "bpolys": self.bpolys,
                "groupByKey": k,
                "groupByValues": v,
                "types": "node,way",
            }  # noqa
            result = requests.get(self.ohsome_api + url, params)
            result = json.loads(result.text)["groupByResult"]
            for gb_result in result:
                for v_s in values_separate:
                    if gb_result["groupByObjectId"] == f"{k}={v_s}":
                        if v_s in density_dict:
                            density_dict[v_s] += gb_result["result"][0]["value"]
                        else:
                            density_dict[v_s] = gb_result["result"][0]["value"]
                if gb_result["groupByObjectId"] != "remainder":
                    density_dict["density"] += gb_result["result"][0]["value"]

        # query ohsome for keys with one value
        for k, v in key_value_filters.items():
            url = "/elements/count/density"
            params = {
                "bpolys": self.bpolys,
                "keys": k,
                "values": v,
                "types": "node,way",
            }  # noqa
            result = requests.get(self.ohsome_api + url, params)
            result = json.loads(result.text)["result"][0]
            density_dict["density"] += result["value"]
            if v in density_dict:
                density_dict[v] += result["value"]
            else:
                density_dict[v] = result["value"]

        # query ohsome for keys with no value
        for k in key_filters:
            url = "/elements/count/density"
            params = {"bpolys": self.bpolys, "keys": k, "types": "node,way"}  # noqa
            result = requests.get(self.ohsome_api + url, params)
            result = json.loads(result.text)["result"][0]
            density_dict["density"] += result["value"]
            if k in density_dict:
                density_dict[k] += result["value"]
            else:
                density_dict[k] = result["value"]

        # merge and rename categories
        density_dict["mountain"] = density_dict.pop("peak")
        density_dict["gas_stations"] = density_dict.pop("fuel")
        density_dict["parks"] = density_dict["park"] + density_dict["national_park"]
        density_dict["waterways"] = density_dict["waterway"] + density_dict["water"]
        density_dict["health_fac_pharmacies"] = (
            density_dict["pharmacy"] + density_dict["hospital"]
        )
        density_dict["education"] = (
            density_dict["school"]
            + density_dict["college"]
            + density_dict["university"]
        )
        density_dict["public_safety"] = (
            density_dict["police"] + density_dict["fire_station"]
        )
        density_dict["public_transport"] = (
            density_dict["bus_stop"] + density_dict["station"]
        )

        self.density_per_catgory = density_dict

    def calculate(self):
        logger.info(f"run calculation for {self.name} indicator")
        # compute relative densities
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

        relative_density_dict = {}
        for k, v in self.density_per_category.items():
            if k not in old_keys and k != "density":
                relative_density_dict[k] = round(
                    100 * v / self.density_per_category["density"], 2
                )
        self.results["relative_poi_densities"] = relative_density_dict

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
