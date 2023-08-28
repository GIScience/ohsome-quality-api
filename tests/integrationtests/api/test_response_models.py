import asyncio

import pytest

from ohsome_quality_analyst.api.response_models import (
    CompIndicator,
    IndicatorGeoJSONResponse,
    IndicatorJSONResponse,
)
from ohsome_quality_analyst.indicators.minimal.indicator import Minimal
from tests.integrationtests.utils import oqt_vcr


class TestIndicatorResponseModels:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_minimal, feature_germany_heidelberg):
        indicator = Minimal(topic_minimal, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        return indicator

    def test_indicator_property(self, indicator):
        raw_dict = indicator.as_dict(exclude_label=True)
        CompIndicator(**raw_dict)

    def test_indicator_json_response(self, indicator):
        raw_dict = indicator.as_dict(exclude_label=True)
        result_dict = {"result": [raw_dict]}
        IndicatorJSONResponse(**result_dict)

    def test_indicator_geojson_response(self, indicator):
        feature = indicator.as_feature(exclude_label=True)
        result_dict = {"type": "FeatureCollection", "features": [feature.model_dump()]}
        IndicatorGeoJSONResponse(**result_dict)
