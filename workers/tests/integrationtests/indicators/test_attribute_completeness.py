from dataclasses import dataclass

import pytest

from ohsome_quality_analyst.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)
from tests.integrationtests.utils import oqt_vcr


@pytest.fixture()
def attribute():
    @dataclass
    class MockAttribute:
        filter_: str

    return MockAttribute(filter_="height=* OR building:level=*")


@pytest.fixture()
def indicator(topic_building_count, feature_germany_heidelberg, attribute):
    return AttributeCompleteness(
        topic_building_count, feature_germany_heidelberg, attribute
    )


@oqt_vcr
def test_attribute_completeness(indicator):
    indicator.preprocess()
