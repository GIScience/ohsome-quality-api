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
    url = build_url(layer, endpoint, ratio)
    data = build_data_dict(layer, bpolys, time, ratio)
    logging.info("Query ohsome API.")
    logging.debug("Query URL: " + url)
    logging.debug("Query filter: " + layer.filter)
    logging.debug("Query data: " + json.dumps(data))
    return await query_ohsome_api(url, data)


async def query_ohsome_api(url: str, data: dict):
    # set custom timeout as ohsome API takes a long time (10 minutes) to send an answer
    timeout = httpx.Timeout(5, read=660)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, data=data)

    try:
        resp.raise_for_status()  # Raise for response status codes 4xx and 5xx
    except httpx.HTTPStatusError:
        logging.error("Query ohsome API failed!")
        raise

    # ohsome API response status codes are either 4xx and 5xx or 200
    try:
        return geojson.loads(resp.content)
    except JSONDecodeError:
        # ohsome API can return invalid GeoJSON after streaming of response
        logging.error("Query ohsome API failed!")
        logging.error(
            "Ohsome API returned invalid GeoJSON after streaming of the response. "
            + "The reason is a timeout of the ohsome API."
        )
        raise


async def get_latest_ohsome_timestamp():
    """Get unix timestamp of ohsome from ohsome api."""
    url = "https://api.ohsome.org/v1/metadata"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    timestamp_str = str(resp.json()["extractRegion"]["temporalExtent"]["toTimestamp"])
    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%MZ")
    return timestamp


def build_url(
    layer,
    endpoint: Optional[str] = None,
    ratio: bool = False,
) -> str:
    """Build endpoint URL of ohsome API."""
    ohsome_api = OHSOME_API.removesuffix("/")
    if endpoint is not None:
        url = ohsome_api + "/" + endpoint.removesuffix("/")
    else:
        url = ohsome_api + "/" + layer.endpoint.removesuffix("/")
    if ratio:
        return url + "/" + "ratio"
    return url


def build_data_dict(
    layer,
    bpolys: str,
    time: Optional[str] = None,
    ratio: bool = False,
) -> dict:
    """Build data dictionary for ohsome API query."""
    if ratio:
        data = {"bpolys": bpolys, "filter": layer.filter, "filter2": layer.ratio_filter}
    else:
        data = {"bpolys": bpolys, "filter": layer.filter}

    if time is not None:
        data["time"] = time
    return data
