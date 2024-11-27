from unittest import mock

import pytest

from ohsome_quality_api.utils.exceptions import (
    SizeRestrictionError,
)
from ohsome_quality_api.utils.validators import (
    validate_area,
)


@mock.patch.dict(
    "os.environ",
    {"OQAPI_GEOM_SIZE_LIMIT": "1000"},
    clear=True,
)
def test_validate_area(feature_germany_heidelberg):
    # expect not exceptions
    validate_area(feature_germany_heidelberg)


@mock.patch.dict(
    "os.environ",
    {"OQAPI_GEOM_SIZE_LIMIT": "1"},
    clear=True,
)
def test_validate_area_exception(feature_germany_heidelberg):
    with pytest.raises(SizeRestrictionError):
        validate_area(feature_germany_heidelberg)
