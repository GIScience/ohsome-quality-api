from enum import Enum

from ohsome_quality_analyst.definitions import get_topic_keys

TopicEnum = Enum("TopicEnum", {name: name for name in get_topic_keys()})
