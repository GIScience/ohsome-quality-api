import pytest
from approvaltests import verify

from ohsome_quality_api.topics import definitions, models
from tests.approvaltests_namers import PytestNamer


def test_get_topic_keys():
    names = definitions.get_topic_keys()
    assert isinstance(names, list)


def test_get_valid_topics():
    topics = definitions.get_valid_topics("minimal")
    assert topics == ("minimal",)


def test_load_topic_definition():
    topics = definitions.load_topic_presets()
    for topic in topics:
        assert isinstance(topics[topic], models.Topic)


def test_get_topic_definition():
    topic = definitions.get_topic_preset("minimal")
    assert isinstance(topic, models.Topic)


def test_get_topic_definition_not_found_error():
    with pytest.raises(KeyError):
        definitions.get_topic_preset("foo")
    with pytest.raises(KeyError):
        definitions.get_topic_preset(None)


def test_get_topic_definitions():
    topics = definitions.get_topic_presets()
    assert isinstance(topics, dict)
    for topic in topics.values():
        assert isinstance(topic, models.Topic)


def test_get_topic_definitions_with_project():
    topics = definitions.get_topic_presets("core")
    assert isinstance(topics, dict)
    for topic in topics.values():
        assert isinstance(topic, models.Topic)
        assert topic.project == "core"


def test_get_topic_preset_translated(locale_de):
    topic = definitions.get_topic_preset("minimal")
    verify(topic.model_dump_json(indent=2), namer=PytestNamer())
