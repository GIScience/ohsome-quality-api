from ohsome_quality_api.indicators.corine_comparison.indicator import CorineComparison
from ohsome_quality_api.topics.models import BaseTopic


def test_preprocess(feature_germany_heidelberg):
    topic = BaseTopic(key="forest", name="forest", description="forest")
    indicator = CorineComparison(feature=feature_germany_heidelberg, topic=topic)
    indicator.preprocess()
    assert isinstance(indicator.areas, list)
    assert isinstance(indicator.clc_classes_corine, list)
    assert isinstance(indicator.clc_classes_osm, list)
    assert len(indicator.areas) != 0
    for area in indicator.areas:
        assert area is not None
