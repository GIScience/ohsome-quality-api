from ohsome_quality_analyst.reports import definitions, models


def test_get_report_names():
    names = definitions.get_report_keys()
    assert isinstance(names, list)


def test_get_report_definitions_with_project():
    reports = definitions.get_report_metadata("core")
    assert isinstance(reports, dict)
    for report in reports.values():
        assert isinstance(report, models.ReportMetadata)
        assert report.project == "core"


def test_get_report_definitions():
    reports = definitions.get_report_metadata()
    assert isinstance(reports, dict)
    for report in reports.values():
        assert isinstance(report, models.ReportMetadata)
