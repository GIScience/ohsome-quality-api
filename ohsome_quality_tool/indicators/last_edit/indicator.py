import datetime
import json
from typing import Dict

import pandas as pd
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.definitions import logger


class Indicator(BaseIndicator):
    """The Last Edit Indicator."""

    name = "LAST_EDIT"

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
        # TODO: we should add more categories here
        #   Can we even come up with a pre-defined list of categories
        #   and respective tags, values in OSM
        #   similar to what we've done for critical infrastructures
        categories = {"roads": "highway=*", "amenities": "amenity=*"}
        # TODO: adjust this to real time span
        #   this is to avoid querying too much data during development
        time = "2019-01-01,2020-07-15"

        query_results = ohsome_api.query_ohsome_api(
            endpoint="/contributions/centroid/",
            categories=categories,
            bpolys=json.dumps(self.bpolys),
            time=time,
        )

        preprocessing_results = {}
        for cat in categories.keys():
            df = pd.json_normalize(query_results[cat]["features"])
            df["timestamp"] = pd.to_datetime(df["properties.@timestamp"])
            # TODO: It's not clear what this actually means
            #   for instance it could be that many objects have been edited in the past
            #   e.g. during data creation and
            #   it's normal that not much edits happen later
            #   returning a histogram might give a better picture
            #   there seems to be a big overlap with saturation analysis here
            #   since both analyses are based on the same data
            #   maybe we can merge both indicators into one
            average_last_edit = df["timestamp"].mean()
            preprocessing_results[cat] = average_last_edit

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict) -> Dict:
        logger.info(f"run calculation for {self.name} indicator")

        results = {}
        for cat in preprocessing_results.keys():
            timestamp = preprocessing_results[cat].to_pydatetime()
            difference = datetime.datetime.now(tz=datetime.timezone.utc) - timestamp
            # TODO: find a better way to capture this information
            #   if there are different classes we might better use a dict instead
            #   and then have the message defined there
            #   this will be easier to read and maintain
            if difference > datetime.timedelta(days=1095):
                message = "Most edits happened more than 3 years ago."
            elif difference > datetime.timedelta(days=730):
                message = "Most edits happened more than 2 years ago."
            elif difference > datetime.timedelta(days=365):
                message = "Most edits happened more than 1 year ago."
            else:
                message = "Most edits happened within the last year."

            results[cat] = {
                "average_last_edit": timestamp,
                "difference": difference,
                "message": message,
            }

        return results

    def export_figures(self):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
