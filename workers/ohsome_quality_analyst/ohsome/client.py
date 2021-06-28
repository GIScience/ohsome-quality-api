import datetime
import json
import logging
from json import JSONDecodeError
from typing import Optional

import geojson
import httpx

from ohsome_quality_analyst.utils.definitions import OHSOME_API
from ohsome_quality_analyst.utils.exceptions import OhsomeApiError


# TODO: Add more tests for ohsome package.
async def query(
    layer,
    bpolys: str,
    time: Optional[str] = None,
    endpoint: Optional[str] = None,
    ratio: bool = False,
) -> dict:
    """
    Query ohsome API endpoint with filter.

    Time is one or more ISO-8601 conform timestring(s).
    https://docs.ohsome.org/ohsome-api/v1/time.html
    """
    url = build_url(layer, endpoint, ratio)
    data = build_data_dict(layer, bpolys, time, ratio)
    logging.info("Query ohsome API.")
    logging.debug("Query URL: " + url)
    logging.debug("Query data: " + json.dumps(data))
    return await query_ohsome_api(url, data)


async def query_ohsome_api(url: str, data: dict) -> dict:
    # custom timeout as ohsome API can take a long time to send an answer
    # (up to 10 minutes)
    timeout = httpx.Timeout(5, read=660)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, data=data)

    # ohsome API response status codes are either 4xx and 5xx or 200
    try:
        # Raise for response status codes 4xx and 5xx.
        # This will raise an error (400) in case of invalid time parameter.
        resp.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise OhsomeApiError(
            "Querying the ohsome API failed! " + error.response.json()["message"]
        ) from error

    try:
        return geojson.loads(resp.content)
    except JSONDecodeError as error:
        raise OhsomeApiError(
            "Ohsome API returned invalid GeoJSON after streaming of the response. "
            + "The reason is a timeout of the ohsome API."
        ) from error


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
    ohsome_api = OHSOME_API.rstrip("/")
    if endpoint is None:
        endpoint = layer.endpoint
    url = ohsome_api + "/" + endpoint.rstrip("/")
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
    data = {"bpolys": bpolys, "filter": layer.filter}
    if ratio:
        if layer.ratio_filter is None:
            raise ValueError(
                "Layer '{0}' has not 'ratio_filter' defined.".format(layer.name)
            )
        else:
            data["filter2"] = layer.ratio_filter
    if time is not None:
        data["time"] = time
    return data
