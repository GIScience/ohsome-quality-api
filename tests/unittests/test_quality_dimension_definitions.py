import pytest
from pytest_approval.main import verify

from ohsome_quality_api.quality_dimensions import definitions
from ohsome_quality_api.quality_dimensions.models import QualityDimension


@pytest.fixture(params=["minimal", "completeness", "currentness"])
def valid_quality_dimension_keys(request):
    return request.param


def test_get_quality_dimensions():
    qds = definitions.get_quality_dimensions()
    assert isinstance(qds, dict)
    for key, qd in qds.items():
        assert isinstance(key, str)
        assert isinstance(qd, QualityDimension)


def test_get_quality_dimension(valid_quality_dimension_keys):
    qd = definitions.get_quality_dimension(valid_quality_dimension_keys)
    assert isinstance(qd, QualityDimension)


def test_get_quality_dimension_wrong_key():
    with pytest.raises(KeyError):
        definitions.get_quality_dimension("foo")


def test_get_quality_dimension_keys_type():
    keys = definitions.get_quality_dimension_keys()
    assert isinstance(keys, list)
    for key in keys:
        assert isinstance(key, str)


def test_get_quality_dimension_keys_valid(valid_quality_dimension_keys):
    keys = definitions.get_quality_dimension_keys()
    assert valid_quality_dimension_keys in keys


def test_get_quality_dimension_translated(locale_de):
    qd = definitions.get_quality_dimension("minimal")
    assert verify(qd.model_dump_json(indent=2))
