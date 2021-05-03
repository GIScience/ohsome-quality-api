import datetime
import json
import logging
from json import JSONDecodeError
from typing import Dict, Optional

import geojson
import httpx

from ohsome_quality_analyst.geodatabase.client import get_hex_ids
from ohsome_quality_analyst.utils.definitions import OHSOME_API, OHSOME_HEX_API


# TODO: Add documentation on time string format.
# TODO: Add tests for ohsome package, including time = None leading to errors
async def query(
    layer,
    bpolys: str,
    time: Optional[str] = None,
    endpoint: Optional[str] = None,
    ratio: bool = False,
) -> Optional[Dict]:
    """Query ohsome API or ohsomeHEX API."""
    if layer.hex_endpoint is not None and endpoint is None:
        response = await hex_query(layer, bpolys, 12)
        if response is not None:
            return response

    return await ohsome_query(layer, bpolys, time, endpoint, ratio)


async def ohsome_query(
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


async def hex_query(layer, bpolys: str, zoomlevel: int) -> Optional[Dict]:
    """Query ohsome API endpoint with filter."""

    url = OHSOME_HEX_API + layer.hex_endpoint + "{}".format(zoomlevel) + "?ids="

    ids = await get_hex_ids(json.loads(bpolys), zoomlevel)
    logging.info("Query ohsomeHEX API.")
    len_ids = len(ids)
    for x, id in enumerate(ids):
        url += str(id)
        if x != len_ids - 1:
            url += "%2C%20"
    # set custom timeout as ohsome API takes a long time to send an answer
    timeout = httpx.Timeout(5, read=600)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url)

    logging.info("Query ohsomeHEX API.")
    logging.debug("Query URL: " + url)
    logging.debug("Query Filter: " + layer.filter)
    if resp.status_code == 200:
        try:
            logging.info("OhsomeHEX query successful!")
            logging.debug(
                "Query response: " + json.dumps(resp.json(), indent=4, sort_keys=True)
            )
            return geojson.loads(resp.content)
        except JSONDecodeError:
            logging.warning("OhsomeHEX query failed!")
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
