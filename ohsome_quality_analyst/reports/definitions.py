from enum import Enum

from ohsome_quality_analyst.definitions import load_metadata
from ohsome_quality_analyst.projects.definitions import ProjectEnum
from ohsome_quality_analyst.reports.models import ReportMetadata


def get_report_names() -> list[str]:
    return list(load_metadata("reports").keys())


ReportEnum = Enum("ReportEnum", {name: name for name in get_report_names()})


def get_report_definitions(project: ProjectEnum = None) -> dict[str, ReportMetadata]:
    reports = load_metadata("reports")
    if project is not None:
        return {k: v for k, v in reports.items() if project in v.projects}
    else:
        return reports


def get_report_classes() -> dict:
    """Map report name to corresponding class."""
    raise NotImplementedError(
        "Use utils.definitions.load_indicator_metadata() and"
        + "utils.helper.name_to_class() instead"
    )
