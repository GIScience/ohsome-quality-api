from datetime import datetime

import asyncpg_recorder
import pytest
import pytest_asyncio
from approvaltests import Options, verify_as_json
from pydantic_core import to_jsonable_python

from ohsome_quality_api.indicators.user_activity.indicator import UserActivity
from tests.approvaltests_namers import PytestNamer
from tests.approvaltests_reporters import PlotlyDiffReporter
from tests.integrationtests.utils import oqapi_vcr


@pytest.mark.asyncio(loop_scope="class")
class TestPreprocess:
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess(
        self,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        indicator = UserActivity(topic_building_count, feature_germany_heidelberg)
        await indicator.preprocess()
        assert len(indicator.bin_total.users_abs) > 0
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


@pytest.mark.asyncio
class TestFigure:
    @pytest_asyncio.fixture(params=[False, True])
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = UserActivity(topic_building_count, feature_germany_heidelberg)
        await i.preprocess()
        i.calculate()
        i.create_figure()
        return i

    async def test_create_figure(self, indicator):
        assert isinstance(indicator.result.figure, dict)
        verify_as_json(
            to_jsonable_python(indicator.result.figure),
            options=Options()
            .with_reporter(PlotlyDiffReporter())
            .with_namer(PytestNamer()),
        )
