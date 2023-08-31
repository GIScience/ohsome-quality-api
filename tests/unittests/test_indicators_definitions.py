from ohsome_quality_api.indicators import definitions, models


def test_get_indicator_names():
    names = definitions.get_indicator_keys()
    assert isinstance(names, list)


def test_get_valid_indicators():
    indicators = definitions.get_valid_indicators("building-count")
    assert indicators == ("mapping-saturation", "currentness", "attribute-completeness")


def test_get_indicator_definitions():
    indicators = definitions.get_indicator_metadata()
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, models.IndicatorMetadata)


def test_get_indicator_definitions_with_project():
    indicators = definitions.get_indicator_metadata("core")
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, models.IndicatorMetadata)
        assert indicator.projects == ["core"]
