from ohsome_quality_tool.utils.config import POSTGRES_DB
from ohsome_quality_tool.utils.definitions import Indicators, logger

logger.info("hello")

print(f"postgres db name: {POSTGRES_DB}")


indicator = Indicators.BUILDING_COMPLETENESS.constructor()
indicator.run()
