from contextvars import ContextVar

import pytest
from pydantic import ValidationError

from ohsome_quality_api.api.request_context import RequestContext
from ohsome_quality_api.api.request_models import IndicatorRequest
from ohsome_quality_api.topics.definitions import get_topic_preset


@pytest.fixture(autouse=True, params=get_topic_preset("custom-topic").indicators)
def mock_request_context_minimal(request, monkeypatch):
    """Mock request context for /indicators/{key}."""
    request_context: ContextVar[RequestContext] = ContextVar("request_context")
    request_context.set(RequestContext(path_parameters={"key": request.param}))
    monkeypatch.setattr(
        "ohsome_quality_api.api.request_models.request_context", request_context
    )


def test_indicator_request_invalid_topic_key(bpolys):
    with pytest.raises(ValidationError):
        IndicatorRequest(
            bpolys=bpolys,
            topic="test-topic",  # invalid
            topic_title="custom-topic",
            topic_filter="building=yes and geometry:point",
        )


def test_indicator_request_missing_filter_and_title(bpolys):
    with pytest.raises(ValidationError):
        IndicatorRequest(
            bpolys=bpolys,
            topic="custom-topic",  # missing filter and title
        )


def test_indicator_request_invalid_missing_filter(bpolys):
    with pytest.raises(ValidationError):
        IndicatorRequest(
            bpolys=bpolys,
            topic="custom-topic",
            topic_title="Custom Topic",
        )


def test_indicator_request_valid(bpolys):
    IndicatorRequest(
        bpolys=bpolys,
        topic="custom-topic",  # valid
        topic_title="my-custom-topic",
        topic_filter="building=yes and geometry:point",
    )


def test_indicator_request_invalid_topic_key_with_filter(bpolys):
    with pytest.raises(ValidationError):
        IndicatorRequest(
            bpolys=bpolys,
            topic="minimal",  # valid
            # not valid in combination w/ existing topic key
            topic_title="custom-topic",
            topic_filter="building=yes and geometry:point",
        )
