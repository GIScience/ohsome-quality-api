from ohsome_quality_api.indicators.corine_comparison.indicator import CorineComparison
from ohsome_quality_api.topics.models import BaseTopic


def test_preprocess(feature_germany_heidelberg):
    topic = BaseTopic(key="forest", name="forest", description="forest")
    indicator = CorineComparison(feature=feature_germany_heidelberg, topic=topic)
    assert indicator is not None
