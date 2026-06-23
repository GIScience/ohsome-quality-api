from typing import Literal

import httpx

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.utils.exceptions import OhsomeApiError

# TODO: extract to config
BASE_URL = "https://staging-ohsome-api.heigitk8s.de/"


async def request(
    url: str,
    method: Literal["get", "post"],
    json: dict | None = None,
) -> dict:
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


async def currentness(
    aoi: dict,
    measure: str,
    ohsome_filter: str,
    time_bins: dict,
) -> dict:
    """Query the ohsome API.

    Raises:
        OhsomeApiError: In case of any response except 2xx status codes.
    """
    url = f"{BASE_URL}/currentness/{measure}.json"
    response = await request(
        url,
        method="post",
        json={"filter": ohsome_filter, "aoi": aoi, "timeBins": time_bins},
    )
    return response["result"]


async def activity_users(
    aoi: dict,
    ohsome_filter: str,
    time_bins: dict,
) -> dict:
    """Query the ohsome API.

    Raises:
        OhsomeApiError: In case of any response except 2xx status codes.
    """
    url = f"{BASE_URL}/activity/users.json"
    response = await request(
        url,
        method="post",
        json={"filter": ohsome_filter, "aoi": aoi, "timeBins": time_bins},
    )
    return response["result"]
