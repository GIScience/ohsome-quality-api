import datetime
import json
from functools import singledispatch
from typing import Optional, Union

import geojson
import httpx
from dateutil.parser import isoparse
from geojson import Feature, FeatureCollection
from schema import Or, Schema, SchemaError, Use

# `geojson` uses `simplejson` if it is installed
try:
    from simplejson import JSONDecodeError
except ImportError:
    from json import JSONDecodeError

from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.base.layer import LayerData, LayerDefinition
from ohsome_quality_analyst.utils.definitions import OHSOME_API, USER_AGENT
from ohsome_quality_analyst.utils.exceptions import LayerDataSchemaError, OhsomeApiError


@singledispatch
async def query(layer) -> dict:
    """Query ohsome API."""
    raise NotImplementedError(
        "Cannot query ohsome API for Layer of type: " + str(type(layer))
    )


@query.register
async def _(
    layer: LayerDefinition,
    bpolys: Union[Feature, FeatureCollection],
    time: Optional[str] = None,
    ratio: Optional[bool] = False,
    group_by: Optional[bool] = False,
    contributions: Optional[bool] = False,
) -> dict:
    """Query ohsome API with given Layer definition and arguments.

    Args:
        layer: Layer definition with ohsome API endpoint and parameters.
        bpolys: Feature for a single bounding (multi)polygon.
            FeatureCollection for "group by boundaries" queries. In this case the
            argument 'group_by' needs to be set to 'True'.
        time: One or more ISO-8601 conform timestring(s) as accepted by the ohsome API.
        ratio: Ratio of OSM elements. The Layer definition needs to have a second
            filter defined.
        group_by: Group by boundary.
        contributions:  Count of the latest contributions provided to the OSM data.
    """

    url = build_url(layer, ratio, group_by, contributions)
    data = build_data_dict(layer, bpolys, time, ratio)
    response = await query_ohsome_api(url, data)
    return validate_query_results(response, ratio, group_by)


@query.register
async def _(
    layer: LayerData,
    bpolys: Union[Feature, FeatureCollection],
    ratio: Optional[bool] = False,
    group_by: Optional[bool] = False,
    **_kargs,
) -> dict:
    """Validate data attached to the Layer object and return data.

    Data will only be validated and returned immediately.
    The ohsome API will not be queried.

    Args:
        layer: Layer with name, description and data attached to it.
        bpolys: Feature for a single bounding (multi)polygon.
            FeatureCollection for "group by boundaries" queries. In this case the
            argument 'group_by' needs to be set to 'True'.
        ratio: Ratio of OSM elements. The Layer definition needs to have a second
            filter defined.
        group_by: Group by boundary.
    """
    try:
        return validate_query_results(layer.data, ratio, group_by)
    except SchemaError as error:
        raise LayerDataSchemaError(
            "Invalid Layer data input to the Mapping Saturation Indicator.",
            error,
        )


async def query_ohsome_api(url: str, data: dict) -> dict:
    """Query the ohsome API.

    A custom connection timeout is set since the ohsome API can take a long time to
    send an answer (< 10 minutes).

    Raises:
        OhsomeApiError: In case of 4xx and 5xx response status codes or invalid
            response due to timeout during streaming.

    """
    async with httpx.AsyncClient(timeout=httpx.Timeout(300, read=660)) as client:
        resp = await client.post(
            url,
            data=data,
            headers={"user-agent": USER_AGENT},
        )
    try:
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


async def get_latest_ohsome_timestamp() -> datetime.datetime:
    """Get latest unix timestamp from the ohsome API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url=OHSOME_API.rstrip("/") + "/metadata",
            headers={"user-agent": USER_AGENT},
        )
    strtime = resp.json()["extractRegion"]["temporalExtent"]["toTimestamp"]
    return datetime.datetime.strptime(strtime, "%Y-%m-%dT%H:%MZ")


def build_url(
    layer: Layer,
    ratio: bool = False,
    group_by: bool = False,
    contributions: bool = False,
):
    if contributions:
        return OHSOME_API.rstrip("/") + "/contributions/latest/count"
    url = OHSOME_API.rstrip("/") + "/" + layer.endpoint.rstrip("/")
    if ratio:
        url += "/ratio"
    if group_by:
        url += "/groupBy/boundary"
    return url


def build_data_dict(
    layer: Layer,
    bpolys: Union[Feature, FeatureCollection],
    time: Optional[str] = None,
    ratio: Optional[bool] = False,
) -> dict:
    """Build data dictionary for ohsome API query.

    Raises:
        TypeError: If 'bpolys' is not of type Feature or FeatureCollection.
    """
    data = {"filter": layer.filter_}
    if isinstance(bpolys, Feature):
        data["bpolys"] = json.dumps(FeatureCollection([bpolys]))
    elif isinstance(bpolys, FeatureCollection):
        data["bpolys"] = json.dumps(bpolys)
    else:
        raise TypeError("Parameter 'bpolys' does not have expected type.")
    if time is not None:
        data["time"] = time
    if ratio:
        data["filter2"] = layer.ratio_filter
    return data


def validate_query_results(
    response: dict,
    ratio: bool = False,
    group_by: bool = False,
) -> dict:
    """Validate query results.

    Raises:
        SchemaError: Error during Schema validation.
    """
    if ratio and group_by:
        Schema(
            {
                "groupByResult": [
                    {
                        "ratioResult": [
                            {
                                "ratio": Or(float, int, "NaN"),
                                "value": Or(float, int),
                                "value2": Or(float, int),
                                "timestamp": Use(lambda t: isoparse(t)),
                            }
                        ],
                        "groupByObject": str,
                    },
                ],
            },
            ignore_extra_keys=True,
        ).validate(response)
        if not response["groupByResult"]:
            raise SchemaError("Empty result field")
    elif ratio:
        Schema(
            {
                "ratioResult": [
                    {
                        "ratio": Or(float, int, "NaN"),
                        "value": Or(float, int),
                        "value2": Or(float, int),
                        "timestamp": Use(lambda t: isoparse(t)),
                    }
                ]
            },
            ignore_extra_keys=True,
        ).validate(response)
        if not response["ratioResult"]:
            raise SchemaError("Empty result field")
    elif group_by:
        Schema(
            {
                "groupByResult": [
                    {
                        "result": [
                            {
                                "value": Or(float, int),
                                Or("timestamp", "fromTimestamp", "toTimestamp"): Use(
                                    lambda t: isoparse(t)
                                ),
                            }
                        ],
                        "groupByObject": str,
                    },
                ],
            },
            ignore_extra_keys=True,
        ).validate(response)
        if not response["groupByResult"]:
            raise SchemaError("Empty result field")
    else:
        Schema(
            {
                "result": [
                    {
                        "value": Or(float, int),
                        Or("timestamp", "fromTimestamp", "toTimestamp"): Use(
                            lambda t: isoparse(t)
                        ),
                    }
                ]
            },
            ignore_extra_keys=True,
        ).validate(response)
        if not response["result"]:
            raise SchemaError("Empty result field")
    return response
