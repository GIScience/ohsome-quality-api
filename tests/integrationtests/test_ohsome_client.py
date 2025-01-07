import asyncio
from datetime import datetime

import pytest

from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.utils.exceptions import OhsomeApiError

from .utils import oqapi_vcr


@oqapi_vcr.use_cassette()
def test_get_latest_ohsome_timestamp():
    time = asyncio.run(ohsome_client.get_latest_ohsome_timestamp())
    assert isinstance(time, datetime)


@oqapi_vcr.use_cassette()
def test_query_ohsome_api_exceptions_404():
    url = "https://api.ohsome.org/v1/elements/lenght"  # length is misspelled
    with pytest.raises(OhsomeApiError, match="Not Found.*"):
        asyncio.run(ohsome_client.query_ohsome_api(url, {}))


@oqapi_vcr.use_cassette
def test_query_ohsome_api_exceptions_400():
    url = "https://api.ohsome.org/v1/elements/length"
    with pytest.raises(OhsomeApiError, match="Invalid filter syntax."):
        asyncio.run(
            ohsome_client.query_ohsome_api(
                url, {"bboxes": "8.67,49.39,8.71,49.42", "filter": "geometry:lie"}
            )
        )
