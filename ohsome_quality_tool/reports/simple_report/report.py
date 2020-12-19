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
    """The remote mapping level one Report."""

    name = "simple-report"
    description = (
        "This report shows the quality for two indicators: "
        "mapping-saturation and ghspop-comparison. "
        "It's main function is to test the interactions between "
        "database, api and website."
    )
    interpretations: Dict = {
        "green": (
            "All indicators show a good quality. "
            "The data in this regions seems to be completely mapped."
        ),
        "yellow": (
            "At least one indicator shows only medium quality. "
            "You should inspect the results for the individual indicators "
            "to identify potential data quality concerns."
        ),
        "red": (
            "The data quality in this region is low. "
            "It is very likely that this regions has not been completely "
            "mapped in OSM."
        ),
    }

    indicator_classes: Dict = get_indicator_classes()
    indicators_definition = [
        (indicator_classes["mapping-saturation"], "building-count"),
        (indicator_classes["ghspop-comparison"], "building-count"),
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
