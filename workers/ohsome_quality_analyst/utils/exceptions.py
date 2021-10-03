"""Custom exception classes"""


class OhsomeApiError(Exception):
    """Request to ohsome API failed"""

    def __init__(self, message):
        self.message = message


class SizeRestrictionError(ValueError):
    """Exception raised if size of input GeoJSON Geometry is too big."""

    def __init__(self, message):
        self.message = message
