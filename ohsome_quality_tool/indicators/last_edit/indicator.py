import json
from typing import Dict

import pandas as pd
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.utils import ohsome_api
from ohsome_quality_tool.utils.config import logger
from ohsome_quality_tool.utils.layers import LEVEL_ONE_LAYERS


class Indicator(BaseIndicator):
    """The Last Edit Indicator."""

    name = "LAST_EDIT"

    def __init__(
        self,
        dynamic: bool,
        layers: Dict = LEVEL_ONE_LAYERS,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
        time_range: str = "2020-01-01,2020-07-15",
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layers=layers,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.time_range = time_range

    def preprocess(self) -> Dict:
        logger.info(f"run preprocessing for {self.name} indicator")

        query_results = ohsome_api.process_ohsome_api(
            endpoint="/contributions/latest/centroid/",
            layers=self.layers,
            bpolys=json.dumps(self.bpolys),
            time=self.time_range,
        )

        preprocessing_results = {}
        for layer in self.layers.keys():
            df = pd.json_normalize(query_results[layer]["features"])
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

            # derive histogram with monthly values
            df.set_index("timestamp", drop=False, inplace=True)
            test = df.groupby(pd.Grouper(freq="M")).agg(
                contributions=pd.NamedAgg(column="timestamp", aggfunc="count")
            )

            preprocessing_results[f"{layer}_avg_last_edit"] = average_last_edit
            preprocessing_results[f"{layer}_histogram"] = test[
                "contributions"
            ].to_numpy()
            preprocessing_results[f"{layer}_timestamps"] = test.index

        return preprocessing_results

    def calculate(self, preprocessing_results: Dict) -> Dict:
        logger.info(f"run calculation for {self.name} indicator")

        results = {
            "data": preprocessing_results,
            "quality_level": "tbd",
            "description": "tbd",
        }

        """
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
        """

        return results

    def export_figures(self, results: Dict):
        # TODO: maybe not all indicators will export figures?
        logger.info(f"export figures for {self.name} indicator")
