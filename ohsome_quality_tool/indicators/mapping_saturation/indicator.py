import json
from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """The Mapping Saturation Indicator."""

    name = "MAPPING_SATURATION"

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
        categories_length = {
            "highways": "highway=*",
        }
        categories_density = {
            "amenities": "amenity=*",
        }
        timespan = "2008-01-01//P1Y"

        query_length = ohsome_api.query_ohsome_api(
            endpoint="/elements/length/",
            categories=categories_length,
            bpolys=json.dumps(self.bpolys),
            time=timespan,
        )

        query_density = ohsome_api.query_ohsome_api(
            endpoint="/elements/count/density/",
            categories=categories_density,
            bpolys=json.dumps(self.bpolys),
            time=timespan,
        )

        preprocessing_results = {**query_length, **query_density}

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict) -> Dict:
        logger.info(f"run calculation for {self.name} indicator")

        # TODO: find better place to store threshold values
        THRESHOLD_MAJOR_CHANGE = 0.25
        THRESHOLD_YELLOW = 0.05
        THRESHOLD_RED = 0.1

        results = {}
        for cat in preprocessing_results.keys():
            results_yearly = [
                y_dict["value"] for y_dict in preprocessing_results[cat]["result"]
            ]

            # calculate slopes between years
            slopes = [0]
            for i in range(1, len(results_yearly)):
                if results_yearly[i - 1] > 0:
                    slopes.append(
                        (results_yearly[i] - results_yearly[i - 1])
                        / results_yearly[i - 1]
                    )

            # determine saturation level
            if max(slopes) < THRESHOLD_MAJOR_CHANGE:
                level = 0
                message = (
                    f"Yearly increase of {cat} features never bigger "
                    f"than {int(THRESHOLD_MAJOR_CHANGE*100)}. "
                    f"There might be a lack of data in this area."
                )
            else:
                last_slope = slopes[-1]
                if last_slope > THRESHOLD_RED:
                    level = 0
                    message = (
                        f"The mapping of {cat} features seems to "
                        "be far from a saturated state."
                    )
                elif last_slope > THRESHOLD_YELLOW:
                    level = 1
                    message = (
                        f"The mapping of {cat} features might not be saturated yet."
                    )
                elif last_slope <= 0:
                    level = 2
                    message = f"The mapping of {cat} features seems to be saturated."

            results[cat] = {
                "slope_last_year": round(last_slope, 2),
                "saturation_level": level,
                "message": message,
            }

        return results

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
