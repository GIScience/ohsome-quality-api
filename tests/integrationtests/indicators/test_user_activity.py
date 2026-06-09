from datetime import datetime

import pytest
from pytest_approval.main import verify_plotly

from ohsome_quality_api.indicators.user_activity.indicator import UserActivity
from tests.integrationtests.utils import oqapi_vcr

pytestmark = pytest.mark.asyncio


@oqapi_vcr.use_cassette
async def test_preprocess(
    topic_building_count,
    feature_germany_heidelberg,
):
    indicator = UserActivity(topic_building_count, feature_germany_heidelberg)
    await indicator.preprocess()
    assert len(indicator.bin_total.users_abs) > 0
    assert isinstance(indicator.result.timestamp, datetime)
    assert isinstance(indicator.result.timestamp_osm, datetime)


@oqapi_vcr.use_cassette
async def test_create_figure(topic_building_count, feature_germany_heidelberg):
    indicator = UserActivity(topic_building_count, feature_germany_heidelberg)
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    assert isinstance(indicator.result.figure, dict)
    assert verify_plotly(indicator.result.figure)
