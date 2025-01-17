import asyncio
import random

import httpx
from pydantic import BaseModel, ConfigDict, field_validator

from ohsome_quality_api.utils.helper import snake_to_lower_camel

# class TrinoQuery:
#         self._query_id: Optional[str] = None
#         self._stats: Dict[Any, Any] = {}
#         self._info_uri: Optional[str] = None
#         self._warnings: List[Dict[Any, Any]] = []
#         self._columns: Optional[List[str]] = None
#         self._finished = False
#         self._cancelled = False
#         self._request = request
#         self._update_type = None
#         self._update_count = None
#         self._next_uri = None
#         self._query = query
#         self._result: Optional[TrinoResult] = None
#         self._legacy_primitive_types = legacy_primitive_types
#         self._row_mapper: Optional[RowMapper] = None
#         self._fetch_mode = fetch_mode


TRINO_HOST = "127.0.0.1"
TRINO_PORT = 8084
TRINO_USER = "mschaub"

URL = f"http://{TRINO_HOST}:{TRINO_PORT}/v1/statement"

HEADERS = {
    "X-Trino-User": TRINO_USER,
}

AUTH = None


class TrinoError(Exception):
    pass


class TrinoTimeoutError(Exception):
    pass


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        frozen=True,
    )


class QueryError(BaseConfig):
    message: str
    error_code: int
    error_name: str
    error_type: str
    failure_info: dict
    error_location: dict[str, int] | None = None


class QueryResults(BaseConfig):
    id: str
    next_uri: str | None = None
    columns: list | None = None
    data: list | None = None
    error: QueryError | None = None

    @field_validator("error")
    @classmethod
    def check_error(cls, value: QueryError) -> str:
        if value is not None:
            raise TrinoError(f"{value.error_name}: {value.message}")
        else:
            return value


async def query(sql) -> QueryResults:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=URL,
            content=sql.encode("utf-8"),
            headers=HEADERS,
        )
    response.raise_for_status()
    results = QueryResults.model_validate(response.json())
    return results


async def raise_for_status(response):
    # TODO: If the client request returns an HTTP 502, 503, or 504, that means
    # there was an intermittent problem processing request and the client
    # should try again in 50-100 ms.

    # TODO: Additionally, if the request returns a 429 status code, the client should retry the request using the Retry-After header value provided.

    # TODO: Any HTTP status other than 502, 503, 504 or 200 means that query processing has failed.
    pass


# TODO: user of fetch() should be able to define a timeout instead wait+attempts.
# A possible solution is to start with very low wait times between attempts and
# scale exponentially for each failure
# TODO: Do we need backoffs and jitter?
# TODO: What is the optimal polling frequency?
async def fetch(
    results: QueryResults,
    wait: int = 1,
    attempts: int = 10,
    _attempt: int = 0,
    _data: tuple = tuple(),
) -> tuple:
    """Fetch all data of a query."""
    # TODO: use one client instance for the eitre fetching/polling
    # intervall
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=results.next_uri,
            headers=HEADERS,
        )
    response.raise_for_status()
    results = QueryResults.model_validate(response.json())

    if results.data is not None:
        _data = _data + tuple(results.data)

    if results.next_uri is None:
        return _data

    elif results.next_uri is not None and _attempt <= attempts:
        # incremental backoff + jitter
        await asyncio.sleep(wait + _attempt + random.random())
        return await fetch(results, _attempt=_attempt + 1, _data=_data)
    else:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url=results.next_uri,
                headers=HEADERS,
            )
        raise TrinoTimeoutError()
