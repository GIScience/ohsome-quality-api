from enum import Enum

from ohsome_quality_analyst.definitions import get_report_names

ReportEnum = Enum("ReportEnum", {name: name for name in get_report_names()})
