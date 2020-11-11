from ohsome_quality_tool.config import POSTGRES_DB
from ohsome_quality_tool.definitions import Indicators, logger

logger.info("hello")

print(f"postgres db name: {POSTGRES_DB}")


indicator = Indicators.BUILDING_COMPLETENESS.constructor()
indicator.run()
