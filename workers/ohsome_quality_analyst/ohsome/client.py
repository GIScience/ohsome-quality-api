import datetime
import json
import logging
from json import JSONDecodeError
from typing import Dict, Optional

import geojson
import httpx

from ohsome_quality_analyst.utils.definitions import OHSOME_API


# TODO: Add documentation on time string format.
# TODO: Add tests for ohsome package, including time = None leading to errors
async def query(
    layer,
    bpolys: str,
    time: Optional[str] = None,
    endpoint: Optional[str] = None,
    ratio: bool = False,
) -> Optional[Dict]:
    """Query ohsome API endpoint with filter."""
    if endpoint is not None:
        url = OHSOME_API + endpoint
    else:
        url = OHSOME_API + layer.endpoint

    if ratio:
        url = url + "/ratio"
        data = {"bpolys": bpolys, "filter": layer.filter, "filter2": layer.ratio_filter}
    else:
        data = {"bpolys": bpolys, "filter": layer.filter}

    if time is not None:
        data["time"] = time

    logging.info("Query ohsome API.")
    logging.debug("Query data: " + json.dumps(data, indent=4, sort_keys=True))

    # set custom timeout as ohsome API takes a long time to send an answer
    timeout = httpx.Timeout(5, read=600)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, data=data)

    logging.info("Query ohsome API.")
    logging.debug("Query URL: " + url)
    logging.debug("Query Filter: " + layer.filter)
    if resp.status_code == 200:
        try:
            logging.info("Ohsome query successful!")
            logging.debug(
                "Query response: " + json.dumps(resp.json(), indent=4, sort_keys=True)
            )
            return geojson.loads(resp.content)
        except JSONDecodeError:
            # ohsome API can return broken GeoJSON during streaming of response
            logging.warning("Ohsome query failed!")
            return None
    elif resp.status_code == 404:
        logging.warning("Query failed!")
        return None


async def get_latest_ohsome_timestamp():
    """Get unix timestamp of ohsome from ohsome api."""
    url = "https://api.ohsome.org/v1/metadata"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    timestamp_str = str(resp.json()["extractRegion"]["temporalExtent"]["toTimestamp"])
    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%MZ")
    return timestamp
