import geojson

from ohsome_quality_tool.utils.config import POSTGRES_DB
from ohsome_quality_tool.utils.definitions import Indicators, logger

logger.info("hello")

print(f"postgres db name: {POSTGRES_DB}")


with open("./data/heidelberg_altstadt.geojson", "r") as file:
    bpolys = geojson.load(file)

indicator = Indicators.BUILDING_COMPLETENESS.constructor(bpolys=bpolys)
indicator.run()
