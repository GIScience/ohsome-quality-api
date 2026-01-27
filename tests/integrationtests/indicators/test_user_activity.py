from datetime import datetime

import asyncpg_recorder
import pytest
import pytest_asyncio
from pytest_approval.main import verify_plotly

from ohsome_quality_api.indicators.user_activity.indicator import UserActivity


@pytest.mark.asyncio(loop_scope="class")
class TestPreprocess:
    @asyncpg_recorder.use_cassette
    async def test_preprocess(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        monkeypatch,
    ):
        # TODO(feature-flag): remove once once ohsome db is in production
        monkeypatch.setenv("OQAPI_OHSOMEDB_ENABLED", "true")
        indicator = UserActivity(topic_building_count, feature_germany_heidelberg)
        await indicator.preprocess()
        assert len(indicator.bin_total.users_abs) > 0
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


@pytest.mark.asyncio
class TestFigure:
    @pytest_asyncio.fixture()
    @asyncpg_recorder.use_cassette
    async def indicator(
        self, topic_building_count, feature_germany_heidelberg, monkeypatch
    ):
        # TODO(feature-flag): remove once once ohsome db is in production
        monkeypatch.setenv("OQAPI_OHSOMEDB_ENABLED", "true")
        i = UserActivity(topic_building_count, feature_germany_heidelberg)
        await i.preprocess()
        i.calculate()
        i.create_figure()
        return i

    async def test_create_figure(self, indicator):
        assert isinstance(indicator.result.figure, dict)
        assert verify_plotly(indicator.result.figure)
