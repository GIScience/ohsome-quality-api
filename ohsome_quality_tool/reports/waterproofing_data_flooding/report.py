from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.definitions import Indicators, logger


class Report(BaseReport):
    """The Waterproofing Data Flooding Report."""

    name = "Waterproofing Data Flooding"

    def __init__(self, bpolys: FeatureCollection) -> None:
        super().__init__(bpolys=bpolys)
        # TODO: check if this structure is good
        #   maybe we want to have an indicator for currentness
        #   and pass the objects as a filter instead
        #   then the definition of which specific saturation to compute
        #   would be passed here in the report
        self.indicators = [Indicators.BUILDING_COMPLETENESS, Indicators.POI_DENSITY]

    def combine_indicators(self):
        logger.info(f"combine indicators for {self.name} report.")
