from ohsome_quality_api.indicators.corine_comparison.indicator import CorineComparison


def test_preprocess():
    indicator = CorineComparison()
    assert indicator is not None
