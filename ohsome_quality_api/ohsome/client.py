import datetime
import json
from functools import singledispatch

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

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.topics.models import BaseTopic as Topic
from ohsome_quality_api.topics.models import TopicData, TopicDefinition
from ohsome_quality_api.utils.exceptions import OhsomeApiError, TopicDataSchemaError


@singledispatch
async def query(topic) -> dict:
    """Query ohsome API."""
    raise NotImplementedError(
        "Cannot query ohsome API for Topic of type: " + str(type(topic))
    )


@query.register
async def _(
    topic: TopicDefinition,
    bpolys: Feature | FeatureCollection,
    time: str | None = None,
    attribute_filter: str | None = None,
    group_by_boundary: bool | None = False,
    count_latest_contributions: bool | None = False,
    density: bool | None = False,
    contribution_type: str | None = None,
) -> dict:
    """Query ohsome API with given Topic definition and arguments.

    Args:
        topic: Topic definition with ohsome API endpoint and parameters.
        bpolys: GeoJSON `Feature` for a single bounding (multi)polygon.
            `FeatureCollection` for "group by boundaries" queries. In this case the
            argument `group_by` needs to be set to `True`.
        time: One or more ISO-8601 conform timestring(s) as accepted by the ohsome API.
        ratio: Ratio of OSM elements. The Topic definition needs to have
            a second filter defined.
        group_by_boundary: Group by boundary.
        count_latest_contributions:  Count of the latest contributions provided to the
            OSM data.
        contribution_type: filters contributions by contribution type: ‘creation’,
            ‘deletion’, ‘tagChange’, ‘geometryChange’ or a combination of them.
    """
    url = build_url(
        topic,
        attribute_filter,
        group_by_boundary,
        count_latest_contributions,
        density,
    )
    data = build_data_dict(topic, bpolys, time, attribute_filter, contribution_type)
    response = await query_ohsome_api(url, data)
    return validate_query_results(response, attribute_filter, group_by_boundary)


@query.register
async def _(
    topic: TopicData,
    bpolys: Feature | FeatureCollection,
    attribute_filter: str | None = False,
    group_by_boundary: bool | None = False,
    **_kargs,
) -> dict:
    """Validate data attached to the Topic object and return data.

    Data will only be validated and returned immediately.
    The ohsome API will not be queried.

    Args:
        topic: Topic with name, description and data attached to it.
        bpolys: Feature for a single bounding (multi)polygon.
            FeatureCollection for "group by boundaries" queries. In this case the
            argument 'group_by' needs to be set to 'True'.
        group_by: Group by boundary.
    """
    try:
        return validate_query_results(topic.data, attribute_filter, group_by_boundary)
    except SchemaError as error:
        raise TopicDataSchemaError(
            "Invalid Topic data input to the Mapping Saturation Indicator.",
            error,
        )


async def query_ohsome_api(url: str, data: dict) -> dict:
    """Query the ohsome API.

    A custom connection timeout is set since the ohsome API can take a long time to
    send an answer (< 10 minutes).

    Raises:
        OhsomeApiError: In case of any response except 2xx status codes or invalid
            response due to timeout during streaming.
    """
    headers = {"user-agent": get_config_value("user_agent")}
    # 660s timeout for reading, and a 300s timeout elsewhere.
    async with httpx.AsyncClient(timeout=httpx.Timeout(300, read=660)) as client:
        resp = await client.post(url, data=data, headers=headers)
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as error:
        # TODO: Make this more general if issue is closed
        # https://github.com/GIScience/ohsome-api/issues/288
        try:
            message = error.response.json()["message"]
        except KeyError:
            message = error.response.json()["error"]
        raise OhsomeApiError("Querying the ohsome API failed! " + message) from error
    try:
        return geojson.loads(resp.content)
    except JSONDecodeError as error:
        raise OhsomeApiError(
            "Ohsome API returned invalid GeoJSON after streaming of the response. "
            + "The reason is a timeout of the ohsome API."
        ) from error


async def get_latest_ohsome_timestamp() -> datetime.datetime:
    """Get latest unix timestamp from the ohsome API."""
    url = get_config_value("ohsome_api").rstrip("/") + "/metadata"
    headers = {"user-agent": get_config_value("user_agent")}
    # 660s timeout for reading, and a 300s timeout elsewhere.
    async with httpx.AsyncClient(timeout=httpx.Timeout(300, read=660)) as client:
        resp = await client.get(url=url, headers=headers)
    strtime = resp.json()["extractRegion"]["temporalExtent"]["toTimestamp"]
    return datetime.datetime.strptime(strtime, "%Y-%m-%dT%H:%MZ")


def build_url(
    topic: Topic,
    attribute_filter: str = None,
    group_by_boundary: bool = False,
    count_latest_contributions: bool = False,
    density: bool = False,
):
    base_url = get_config_value("ohsome_api").rstrip("/")
    if count_latest_contributions:
        return base_url + "/contributions/latest/count"
    url = base_url + "/" + topic.endpoint + "/" + topic.aggregation_type
    if density:
        url += "/density"
    if attribute_filter:
        url += "/ratio"
    if group_by_boundary:
        url += "/groupBy/boundary"
    return url


def build_data_dict(
    topic: Topic,
    bpolys: Feature | FeatureCollection,
    time: str | None = None,
    attribute_filter: str | None = False,
    contribution_type: str | None = None,
) -> dict:
    """Build data dictionary for ohsome API query.

    Raises:
        TypeError: If 'bpolys' is not of type Feature or FeatureCollection.
    """
    data = {"filter": topic.filter}
    if isinstance(bpolys, Feature):
        data["bpolys"] = json.dumps(FeatureCollection([bpolys]))
    elif isinstance(bpolys, FeatureCollection):
        data["bpolys"] = json.dumps(bpolys)
    else:
        raise TypeError(_("Parameter 'bpolys' does not have expected type."))
    if time is not None:
        data["time"] = time
    if attribute_filter:
        data["filter2"] = attribute_filter
    if contribution_type is not None:
        data["contributionType"] = contribution_type
    return data


def validate_query_results(
    response: dict,
    attribute_filter: str = None,
    group_by_boundary: bool = False,
) -> dict:
    """Validate query results.

    Raises:
        SchemaError: Error during Schema validation.
    """
    response_key = "result"
    schema = {
        "result": [
            {
                "value": Or(float, int),
                Or("timestamp", "fromTimestamp", "toTimestamp"): Use(
                    lambda t: isoparse(t)
                ),
            }
        ]
    }
    if attribute_filter:
        schema = {
            "ratioResult": [
                {
                    "value": Or(float, int),
                    "value2": Or(float, int),
                    "ratio": Or(float, int, "NaN"),
                    Or("timestamp", "fromTimestamp", "toTimestamp"): Use(
                        lambda t: isoparse(t)
                    ),
                }
            ]
        }
        response_key = "ratioResult"
    if group_by_boundary:
        schema = {
            "groupByResult": [
                schema,
            ],
        }
        schema["groupByResult"][0]["groupByObject"] = Or(int, str)
        response_key = "groupByResult"
    Schema(
        schema,
        ignore_extra_keys=True,
    ).validate(response)
    if not response[response_key]:
        raise SchemaError("Empty result field")
    return response
