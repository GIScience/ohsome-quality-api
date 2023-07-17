from enum import Enum

from ohsome_quality_analyst.definitions import get_indicator_names

IndicatorEnum = Enum("IndicatorEnum", {name: name for name in get_indicator_names()})
