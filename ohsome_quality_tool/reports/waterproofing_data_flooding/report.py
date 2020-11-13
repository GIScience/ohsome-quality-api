from geojson import FeatureCollection

from ohsome_quality_tool.base.report import BaseReport
from ohsome_quality_tool.utils.definitions import Indicators, logger


class Report(BaseReport):
    """The Waterproofing Data Flooding Report."""

    name = "Waterproofing Data Flooding"
    # TODO: check if this structure is good
    #   maybe we want to have an indicator for currentness
    #   and pass the objects as a filter instead
    #   then the definition of which specific saturation to compute
    #   would be passed here in the report
    indicators = [Indicators.BUILDING_COMPLETENESS, Indicators.POI_DENSITY]

    def __init__(
        self,
        dynamic: bool,
        bpolys: FeatureCollection = None,
        table: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic, bpolys=bpolys, table=table, feature_id=feature_id
        )

    def combine_indicators(self):
        """Combine the individual scores per indicator."""
        logger.info(f"combine indicators for {self.name} report.")
