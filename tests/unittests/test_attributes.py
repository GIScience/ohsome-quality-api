import pytest
from pydantic import ValidationError

from ohsome_quality_api.attributes.models import Attribute


def test_attributes():
    Attribute(
        name="My fancy Attribute", description="some description", filter="testfilter"
    )


def test_attributes_sql_filter():
    Attribute(
        name="My fancy Attribute",
        description="some description",
        filter="testfilter",
        filter_sql="testsqlfilter",
    )


def test_parameter_missing():
    with pytest.raises(ValidationError):
        Attribute(name="some name", description="some description")
    with pytest.raises(ValidationError):
        Attribute(description="description")


def test_extra_parameter():
    with pytest.raises(ValidationError):
        Attribute(
            name="My fancy Attribute",
            description="some description",
            foo="bar",
        )
