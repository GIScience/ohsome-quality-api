from ohsome_quality_api.indicators.attribute_completeness.indicator import AttributeCompleteness


def test_create_description():
    indicator = AttributeCompleteness() # Grundschritte hier setzen
    indicator.result = # nötige result Werte hier setzen
    description = indicator.create_description()
    assert description == "expected text here"