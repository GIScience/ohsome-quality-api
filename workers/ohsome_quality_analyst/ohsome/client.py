import datetime
import logging
from typing import Dict

import httpx

from ohsome_quality_analyst.utils.definitions import OHSOME_API


# TODO: Add documentation on time string format.
# TODO: Add tests for ohsome package, including time = None leading to errors
async def query(layer, bpolys: str, time: str = None, endpoint: str = None) -> Dict:
    """Query ohsome API endpoint with filter."""
    if endpoint:
        url = OHSOME_API + endpoint
    else:
        url = OHSOME_API + layer.endpoint
    data = {"bpolys": bpolys, "filter": layer.filter}
    if time is not None:
        data["time"] = time
    # set custom timeout as ohsome API takes a long time to send an answer
    timeout = httpx.Timeout(5, read=600)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, data=data)

    logging.info("Query ohsome API.")
    logging.debug("Query URL: " + url)
    logging.debug("Query Filter: " + layer.filter)
    if resp.status_code == 200:
        logging.info("Query successful!")
    elif resp.status_code == 404:
        # TODO: Handle when query fails
        logging.info("Query failed!")

    return resp.json()


async def get_latest_ohsome_timestamp():
    """Get unix timestamp of ohsome from ohsome api."""
    url = "https://api.ohsome.org/v1/metadata"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    timestamp_str = str(resp.json()["extractRegion"]["temporalExtent"]["toTimestamp"])
    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%MZ")
    return timestamp
