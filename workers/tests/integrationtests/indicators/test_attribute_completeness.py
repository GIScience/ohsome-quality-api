import asyncio
from dataclasses import dataclass

import pytest

from ohsome_quality_analyst.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)


@pytest.fixture()
def attribute():
    @dataclass
    class MockAttribute:
        filter_: str

    return MockAttribute(filter_="(height=* or building:level=*)")


@pytest.fixture()
def indicator(topic_building_count, feature_germany_heidelberg, attribute):
    return AttributeCompleteness(
        topic_building_count, feature_germany_heidelberg, attribute
    )


def test_attribute_completeness(indicator):
    asyncio.run(indicator.preprocess())
    assert indicator.ratio is not None
