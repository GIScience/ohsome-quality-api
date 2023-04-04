from ohsome_quality_analyst import __version__
from ohsome_quality_analyst.api.response_models import ResponseBase, TopicResponse
from ohsome_quality_analyst.definitions import ATTRIBUTION_URL


def test_response_model():
    response = ResponseBase()
    assert response.api_version == __version__
    assert response.attribution == {"url": ATTRIBUTION_URL}


def test_topic_response_model(topic_building_count):
    response = TopicResponse(result=topic_building_count)
    assert response.result == topic_building_count
