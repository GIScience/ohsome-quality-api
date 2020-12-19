from statistics import mean
from typing import Dict, Tuple

from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.definitions import (
    TrafficLightQualityLevels,
    get_indicator_classes,
    logger,
)


class Report(BaseReport):
    """The Sketchmap Fitness Report."""

    name = "sketchmap-fitness"
    description = (
        "The sketchmap fitness report consists of four data quality indicators "
        "(mapping saturation of major roads, currentness for major-roads and "
        "amenities, density of points-of-interest). The report tells you whether "
        "you will be able to use the Sketch Map Tool for the selected regions."
    )
    interpretations: Dict = {
        "green": (
            "All indicators show a good quality. "
            "This regions seems to be very well suited for mapping "
            "using the Sketch Map Tool."
        ),
        "yellow": (
            "At least one indicator shows only medium or lower quality. "
            "You should inspect the results for the individual indicators "
            "to identify potential data quality concerns."
        ),
        "red": (
            "The data quality in this region is low. "
            "It is very likely that it is not possible to use "
            "the Sketch Map Tool for this area."
        ),
    }

    indicator_classes: Dict = get_indicator_classes()
    indicators_definition = [
        (indicator_classes["mapping-saturation"], "major-roads"),
        (indicator_classes["last-edit"], "major-roads"),
        (indicator_classes["last-edit"], "amenities"),
        (indicator_classes["poi-density"], "points-of-interests"),
    ]

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

    def combine_indicators(
        self, indicators
    ) -> Tuple[TrafficLightQualityLevels, str, str]:
        """Combine the individual scores per indicator."""
        logger.info(f"combine indicators for {self.name} report.")

        # get mean of indicator quality values
        values = []

        for indicator in indicators:
            values.append(indicator["result"]["value"])

        value = mean(values)

        if value < 0.5:
            label = TrafficLightQualityLevels.RED
            text = self.interpretations["red"]
        elif value < 1:
            label = TrafficLightQualityLevels.YELLOW
            text = self.interpretations["yellow"]
        elif value >= 1:
            label = TrafficLightQualityLevels.GREEN
            text = self.interpretations["green"]
        else:
            label = None
            text = "Could not derive quality level"

        return label, value, text
