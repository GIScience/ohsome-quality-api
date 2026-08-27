from typing import Literal

import httpx

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.utils.exceptions import OhsomeApiError

BASE_URL = get_config_value("ohsome_api_url")


async def request(
    url: str,
    method: Literal["get", "post"],
    json: dict | None = None,
) -> dict:
    """Query the ohsome API.

    Raises:
        OhsomeApiError: In case of any response except 2xx status codes.
    """
    headers = {
        "user-agent": get_config_value("user_agent"),
        "authorization": get_config_value("heigit_api_key"),
    }
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(300, read=660),
        verify=False,  # TODO: remove to veriyf SSL certificate  # noqa: S501
    ) as client:
        match method:
            case "get":
                resp = await client.get(url, headers=headers)
            case "post":
                resp = await client.post(url, headers=headers, json=json)
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise OhsomeApiError("Querying the ohsome API failed!") from error

    return resp.json()


async def metadata() -> dict:
    url = BASE_URL + "/metadata"
    return await request(url, method="get")


async def features(
    aoi: dict,
    measure: str,
    ohsome_filter: str,
    time_series: dict,
    clip: bool = False,
):
    url = f"{BASE_URL}/stats/features/{measure}.json"
    response = await request(
        url,
        method="post",
        json={
            "filter": ohsome_filter,
            "aoi": aoi,
            "time": time_series,
            "clip": clip,
        },
    )
    return response["result"]


async def currentness(
    aoi: dict,
    measure: str,
    ohsome_filter: str,
    time_bins: dict,
) -> dict:
    url = f"{BASE_URL}/stats/currentness/{measure}.json"
    response = await request(
        url,
        method="post",
        json={"filter": ohsome_filter, "aoi": aoi, "time": time_bins},
    )
    return response["result"]


async def activity_users(
    aoi: dict,
    ohsome_filter: str,
    time_bins: dict,
) -> dict:
    url = f"{BASE_URL}/stats/contributors/count.json"
    response = await request(
        url,
        method="post",
        json={"filter": ohsome_filter, "aoi": aoi, "time": time_bins},
    )
    return response["result"]
