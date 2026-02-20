import logging
import os

import rpy2.rinterface_lib.callbacks

__version__ = "1.15.0"
__title__ = "ohsome quality API"
__description__ = "Data quality estimations for OpenStreetMap"
__author__ = "ohsome team"
__email__ = "ohsome@heigit.org"
__homepage__ = "https://api.quality.ohsome.org/"

logging.basicConfig(
    level=os.getenv("OQAPI_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s",
)
logger = logging.getLogger("ohsome_quality_api")
logger.info("INFO level logs enabled")
logger.debug("DEBUG level logs enabled")


class RPY2LoggingFilter(logging.Filter):  # Sensitive
    def filter(self, record):
        return " library ‘/usr/share/R/library’ contains no packages" in record.msg


# Avoid R library contains no packages WARNING logs.
# OQAPI has no dependencies on additional R libraries.
rpy2.rinterface_lib.callbacks.logger.addFilter(RPY2LoggingFilter())

# Avoid a huge amount of DEBUG logs from matplotlib font_manager.py
logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)
