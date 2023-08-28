import pytest
from pydantic import ValidationError

from ohsome_quality_api.quality_dimensions.models import QualityDimension


def test_quality_dimension():
    QualityDimension(name="My fancy QualityDimension", description="some description")


def test_parameter_missing():
    with pytest.raises(ValidationError):
        QualityDimension(name="some name")
    with pytest.raises(ValidationError):
        QualityDimension(description="description")


def test_extra_parameter():
    with pytest.raises(ValidationError):
        QualityDimension(
            name="My fancy QualityDimension",
            description="some description",
            foo="bar",
        )
