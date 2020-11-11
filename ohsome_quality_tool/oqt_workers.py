import geojson

from ohsome_quality_tool.utils.definitions import Indicators, Reports, logger

logger.info("hello")

with open("./data/heidelberg_altstadt.geojson", "r") as file:
    bpolys = geojson.load(file)

indicator = Indicators.BUILDING_COMPLETENESS.constructor(bpolys=bpolys)
indicator.run()

report = Reports.WATERPROOFING_DATA_FLOODING.constructor(bpolys=bpolys)
report.run()
