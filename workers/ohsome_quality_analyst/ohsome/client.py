import datetime
from typing import Dict

import requests

from ohsome_quality_analyst.utils.definitions import OHSOME_API, logger


# TODO: Add documentation on time string format.
def query(layer, bpolys: str, time: str = None, endpoint: str = None) -> Dict:
    """Query ohsome API endpoint with filter."""
    if endpoint:
        url = OHSOME_API + endpoint
    else:
        url = OHSOME_API + layer.endpoint
    data = {"bpolys": bpolys, "filter": layer.filter, "time": time}
    response = requests.post(url, data=data)

    logger.info("Query ohsome API.")
    logger.info("Query URL: " + url)
    logger.info("Query Filter: " + layer.filter)
    if response.status_code == 200:
        logger.info("Query successful!")
    elif response.status_code == 404:
        logger.info("Query failed!")

    return response.json()


def get_latest_ohsome_timestamp():
    """Get unix timestamp of ohsome from ohsome api."""
    url = "https://api.ohsome.org/v1/metadata"
    r = requests.get(url)
    timestamp_str = str(r.json()["extractRegion"]["temporalExtent"]["toTimestamp"])
    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%MZ")
    return timestamp
