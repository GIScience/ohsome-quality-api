"""Custom exception classes"""


class Error(Exception):
    """Base class for exceptions in this module."""


class OhsomeApiError(Error):
    """Request to ohsome API failed"""

    pass


class SizeRestrictionError(ValueError):
    """Exception raised if size of input GeoJSON Geometry is too big."""

    def __init__(self, message):
        self.message = message

    pass
